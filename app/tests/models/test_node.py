
import datetime
from app.tests.test_base import TestBase
from unittest.mock import patch

from app import db

import sqlalchemy

from app.models.node import Node, BU_VERSION
from app.service_objects.aws_node_manager import AWSNodeManager
from app.service_objects.digital_ocean_node_manager import DigitalOceanNodeManager

class TestNode(TestBase):
    def test_node(self):
        """
        Test the creation of Node records
        """
        node_one = Node(provider='aws', name="Bob's node")
        node_two = Node(provider='digital_ocean', name="Bob's node")

        db.session.add(node_one)
        db.session.add(node_two)
        db.session.commit()

        self.assertEqual(Node.query.count(), 2)

    def test_node_provider_allowed(self):
        """
        Test that a Node's provider field must be included in 'aws' or 'digital_ocean'
        """
        with self.assertRaises(AssertionError):
            node = Node(provider='linode', name="Bob's node")

    def test_node_manager(self):
        """
        Test that the right node manager is used, given the node's provider.
        """
        node_one = Node(provider='aws', name="Bob's node")
        self.assertEqual(node_one.node_manager().__class__, AWSNodeManager)

        node_two = Node(provider='digital_ocean', name="Bob's node")
        self.assertEqual(node_two.node_manager().__class__, DigitalOceanNodeManager)

    @patch('app.models.node.configure_node')
    @patch('app.models.node.DigitalOceanNodeManager')
    @patch('app.models.node.AWSNodeManager')
    def test_provision(self, mock_aws_node_manager, mock_digital_ocean_node_manager, mock_configure_task):
        """
        Test that:
        1) The correct node manager is used to provision an instance.
        2) The launched_at value for the node is updated.
        3) A celery task to configure the node is queued for 45 minutes from now.
        """
        node = Node(provider='digital_ocean', name="Bob's node")
        node_manager = mock_digital_ocean_node_manager.return_value

        self.assertEqual(node.launched_at, None)

        node.provision()

        node_manager.create_server_from_latest_snapshot.assert_called()
        self.assertTrue(datetime.datetime.now(datetime.timezone.utc) - node.launched_at < datetime.timedelta(minutes=1))
        mock_configure_task.apply_async.assert_called_with(args=(node.id,), countdown=1800)

    @patch('app.models.node.configure_node')
    @patch('app.models.node.DigitalOceanNodeManager')
    @patch('app.models.node.AWSNodeManager')
    def test_rebuild(self, mock_aws_node_manager, mock_digital_ocean_node_manager, mock_configure_task):
        """
        Test that:
        1) The correct node manager is used to provision an instance.
        2) A celery task to configure the node is queued for 45 minutes from now.
        3) The Node's bu_version attribute is updated to reflect the latest value in models/node.py.
        """
        node = Node(provider='digital_ocean', name="Bob's node", bu_version='0.3' ,status='off')
        db.session.add(node)
        db.session.commit()
        self.assertEqual(node.bu_version, '0.3')

        node_manager = mock_digital_ocean_node_manager.return_value

        node.rebuild()

        node_manager.rebuild_server_from_latest_snapshot.assert_called()
        mock_configure_task.apply_async.assert_called_with(args=(node.id,), countdown=1800)
        self.assertEqual(node.bu_version, BU_VERSION)

    @patch('app.models.node.DigitalOceanNodeManager')
    @patch('app.models.node.AWSNodeManager')
    def test_configure(self, aws_node_manager, digital_ocean_node_manager):
        """
        Test that message is relayed to the appropriate node manager.
        """
        node = Node(provider='aws', name="Bob's node", status='provisioned')
        aws_manager_instance = aws_node_manager.return_value
        node.configure()
        aws_node_manager.assert_called()
        aws_manager_instance.update_bitcoin_conf.assert_called()
        digital_ocean_node_manager.assert_not_called()
