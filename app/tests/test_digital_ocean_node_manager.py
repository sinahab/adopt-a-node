
from .test_base import TestBase
from unittest.mock import patch, MagicMock

from app import db
from app.models.node import Node
from app.service_objects.digital_ocean_node_manager import DigitalOceanNodeManager

from app.tests.support.fake_digital_ocean_manager import FakeDigitalOceanManager

class TestDigitalOceanNodeManager(TestBase):

    @patch('app.service_objects.digital_ocean_node_manager.Manager')
    def test_rebuild_server_from_latest_snapshot(self, mock_do_manager_class):
        """
        Test that the current droplet is rebuilt from the latest snapshot
        """

        node = Node(provider='digital_ocean', provider_id='droplet123')

        mock_do_manager = mock_do_manager_class.return_value
        mock_do_manager.get_droplet_snapshots.return_value = FakeDigitalOceanManager(token='asd123').get_droplet_snapshots()
        mock_droplet = mock_do_manager.get_droplet.return_value

        DigitalOceanNodeManager(node).rebuild_server_from_latest_snapshot()

        mock_do_manager.get_droplet.assert_called_with(node.provider_id)
        mock_droplet.rebuild.assert_called_with(image_id='456') # value from FakeDigitalOceanManager


    @patch('app.service_objects.digital_ocean_node_manager.Manager')
    def test_get_latest_snapshot(self, mock_do_manager_class):
        """
        Test that it gets and returns the latest snapshot object from Digital Ocean
        """

        node = Node(provider='digital_ocean')

        mock_do_manager_class.return_value = FakeDigitalOceanManager(token='asdf')
        mock_manager = mock_do_manager_class.return_value

        latest_snapshot = DigitalOceanNodeManager(node).get_latest_snapshot()

        mock_do_manager_class.assert_called()
        # values from FakeDigitalOceanManager
        self.assertEqual(latest_snapshot.id, '456')
