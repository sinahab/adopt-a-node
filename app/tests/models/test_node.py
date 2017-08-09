
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

    @patch('app.models.node.install_bitcoind')
    @patch('app.models.node.DigitalOceanNodeManager')
    @patch('app.models.node.AWSNodeManager')
    def test_provision(self, mock_aws_node_manager, mock_digital_ocean_node_manager, mock_install_task):
        """
        Test that:
        1) The correct node manager is used to provision an instance.
        2) A celery task to install bitcoind on the node is queued for 1 minute from now.
        """
        node = Node(provider='digital_ocean', name="Bob's node")
        db.session.add(node)
        db.session.commit()
        node_manager = mock_digital_ocean_node_manager.return_value

        self.assertEqual(node.launched_at, None)

        node.provision()

        node_manager.create_server.assert_called()
        mock_install_task.apply_async.assert_called_with(args=(node.id,), countdown=120)

    @patch('app.models.node.install_bitcoind')
    @patch('app.models.node.DigitalOceanNodeManager')
    @patch('app.models.node.AWSNodeManager')
    def test_provision_existing(self, mock_aws_manager_class, mock_do_manager_class, mock_install_task):
        """
        Test that it raises an exception when the node already has an associated server.
        """
        node = Node(provider='digital_ocean', name="Bob's node", provider_id='123')
        db.session.add(node)
        db.session.commit()
        do_manager = mock_do_manager_class.return_value

        node.provision()

        do_manager.create_server.assert_not_called()
        mock_install_task.apply_async.assert_not_called()

    @patch('app.models.node.configure_node')
    @patch('app.models.node.DigitalOceanNodeManager')
    @patch('app.models.node.AWSNodeManager')
    def test_install(self, aws_node_manager, digital_ocean_node_manager, mock_configure_task):
        """
        Test that:
        1) it installs bitcoind
        2) opens port 8333
        3) schedules a Celery task to configure the node in 30 minutes.
        """
        node = Node(provider='aws', name="Bob's node", status='provisioned')
        db.session.add(node)
        db.session.commit()
        aws_manager_instance = aws_node_manager.return_value

        node.install()

        aws_node_manager.assert_called()
        aws_manager_instance.install_bitcoind.assert_called()
        aws_manager_instance.open_bitcoind_port.assert_called()
        mock_configure_task.apply_async.assert_called_with(args=(node.id,), countdown=1800)
        digital_ocean_node_manager.assert_not_called()

    @patch('app.models.node.DigitalOceanNodeManager')
    @patch('app.models.node.AWSNodeManager')
    def test_configure(self, aws_node_manager, digital_ocean_node_manager):
        """
        Test that message is relayed to the appropriate node manager.
        """
        node = Node(provider='aws', name="Bob's node", status='installed')
        db.session.add(node)
        db.session.commit()
        aws_manager_instance = aws_node_manager.return_value

        node.configure()

        aws_node_manager.assert_called()
        aws_manager_instance.update_bitcoin_conf.assert_called()
        digital_ocean_node_manager.assert_not_called()

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
    def test_expire_successful(self, mock_aws_manager_class, mock_do_manager_class):
        """
        Test that the node status is set to 'expired',
        and that the node is deleted on the according cloud provider.
        """
        node = Node(provider='digital_ocean', name="mynode", bu_version='0.3' , status='up')
        db.session.add(node)
        db.session.commit()

        mock_do_manager = mock_do_manager_class.return_value
        mock_do_manager.destroy_server.return_value = True

        node.expire()

        mock_do_manager.destroy_server.assert_called()
        n = Node.query.filter_by(name='mynode').all()[0]
        self.assertEqual(n.status, 'expired')
        self.assertEqual(n.provider_status, 'expired_by_adoptanode')

    @patch('app.models.node.DigitalOceanNodeManager')
    @patch('app.models.node.AWSNodeManager')
    def test_expire_unsuccessful(self, mock_aws_manager_class, mock_do_manager_class):
        """
        Test that the node status is set to 'expired',
        and that the node is deleted on the according cloud provider.
        """
        node = Node(provider='digital_ocean', name="mynode", bu_version='0.3' , status='up')
        db.session.add(node)
        db.session.commit()

        mock_do_manager = mock_do_manager_class.return_value
        mock_do_manager.destroy_server.return_value = False

        node.expire()

        mock_do_manager.destroy_server.assert_called()
        n = Node.query.filter_by(name='mynode').all()[0]
        self.assertEqual(n.status, 'up')

    def test_expires_at(self):
        """
        Test that it returns the datetime at which the node expires.
        """
        launched_at = datetime.datetime(2017, 1, 5, 12, 13, 14, tzinfo=datetime.timezone.utc)
        node = Node(
            provider='aws',
            name="Bob's node",
            status='provisioned',
            launched_at=launched_at,
            months_adopted=3
        )
        db.session.add(node)
        db.session.commit()

        expected_expires_at = datetime.datetime(2017, 4, 5, 12, 13, 14, tzinfo=datetime.timezone.utc)

        self.assertEqual(node.expires_at(), expected_expires_at)

    def test_has_expired(self):
        """
        Test that it correctly returns whether the node is expired or not.
        """
        two_days_ago = datetime.datetime.utcnow() - datetime.timedelta(days=2)
        two_months_ago = datetime.datetime.utcnow() - datetime.timedelta(days=60)
        node_one = Node(provider='digital_ocean', status='up', launched_at=two_days_ago, months_adopted=1)
        node_two = Node(provider='digital_ocean', status='up', launched_at=two_months_ago, months_adopted=1)
        db.session.add(node_one)
        db.session.add(node_two)
        db.session.commit()

        self.assertEqual(node_one.has_expired(), False)
        self.assertEqual(node_two.has_expired(), True)
