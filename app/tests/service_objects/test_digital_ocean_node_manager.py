
from app.tests.test_base import TestBase
from unittest.mock import patch, MagicMock
from app.utils.misc import DotDict

import datetime
from app import db
from app.models.node import Node
from app.service_objects.digital_ocean_node_manager import DigitalOceanNodeManager, DIGITAL_OCEAN_REGIONS

from app.tests.support.fake_digital_ocean_manager import FakeManager

class TestDigitalOceanNodeManager(TestBase):

    @patch('app.service_objects.digital_ocean_node_manager.Manager')
    def test_rebuild_server_from_latest_snapshot(self, mock_do_manager_class):
        """
        Test that the current droplet is rebuilt from the latest snapshot
        """

        node = Node(provider='digital_ocean', provider_id='droplet123')
        db.session.add(node)
        db.session.commit()

        fake_digital_ocean_manager = FakeManager(token='asd123')

        mock_do_manager = mock_do_manager_class.return_value
        mock_do_manager.get_droplet_snapshots.return_value = fake_digital_ocean_manager.get_droplet_snapshots()
        mock_do_manager.get_droplet.return_value = fake_digital_ocean_manager.get_droplet(node.provider_id)
        mock_droplet = mock_do_manager.get_droplet.return_value

        DigitalOceanNodeManager(node).rebuild_server_from_latest_snapshot()

        mock_do_manager.get_droplet.assert_called_with(node.provider_id)
        # test that provider attributes have been updated from Digital Ocean
        n = Node.query.filter_by(provider_id='droplet123').all()[0]
        self.assertEqual(n.provider_status, 'exploding')

    @patch('app.service_objects.digital_ocean_node_manager.Manager')
    @patch('app.service_objects.digital_ocean_node_manager.Droplet')
    def test_create_server(self, mock_do_droplet_class, mock_do_manager_class):
        """
        Test that it creates a new server
        """
        node = Node(provider='digital_ocean', name='test123')
        db.session.add(node)
        db.session.commit()

        mock_do_droplet = mock_do_droplet_class.return_value
        mock_do_droplet.id = 14123
        mock_do_droplet.region = 'test_region'

        DigitalOceanNodeManager(node).create_server()

        mock_do_droplet_class.assert_called()
        mock_do_droplet.create.assert_called()
        db.session.refresh(node)
        self.assertEqual(node.provider_id, '14123')
        self.assertEqual(node.provider_region, 'test_region')
        self.assertTrue(datetime.datetime.now(datetime.timezone.utc) - node.launched_at < datetime.timedelta(minutes=1))

    @patch('app.service_objects.digital_ocean_node_manager.Manager')
    def test_get_latest_snapshot(self, mock_do_manager_class):
        """
        Test that it gets and returns the latest snapshot object from Digital Ocean
        """

        node = Node(provider='digital_ocean')

        mock_do_manager = mock_do_manager_class.return_value
        mock_do_manager.get_droplet_snapshots.return_value = FakeManager(token='asdf').get_droplet_snapshots()

        latest_snapshot = DigitalOceanNodeManager(node).get_latest_snapshot()

        mock_do_manager_class.assert_called()
        mock_do_manager.get_droplet_snapshots.assert_called()
        # values from FakeManager
        self.assertEqual(latest_snapshot.id, '456')

    @patch('app.service_objects.digital_ocean_node_manager.Manager')
    def test_destroy_server(self, mock_do_manager_class):
        """
        Test that it destroys the droplet
        """
        node = Node(provider='digital_ocean', provider_id='123', status='up')

        mock_manager = mock_do_manager_class.return_value
        mock_manager.get_droplet.return_value = FakeManager(token='asdf').get_droplet(node.provider_id)
        mock_droplet = mock_manager.get_droplet.return_value
        mock_droplet.destroy.return_value = False

        latest_snapshot = DigitalOceanNodeManager(node).destroy_server()

        mock_do_manager_class.assert_called()
        mock_droplet.destroy.assert_called()

    def test_pick_random_region(self):
        """
        Test that it picks a random Digital Ocean region
        """
        node = Node(provider='digital_ocean')

        returned_region = DigitalOceanNodeManager(node)._pick_random_region()
        self.assertTrue(returned_region['name'] in list(map(lambda r: r['name'], DIGITAL_OCEAN_REGIONS)))

        actual_region = list(filter(lambda r: r['name'] == returned_region['name'], DIGITAL_OCEAN_REGIONS))[0]
        self.assertEqual(returned_region['slug'], actual_region['slug'])
