
from .test_base import TestBase
from unittest.mock import patch, MagicMock
from app.utils.misc import DotDict

from app import db
from app.models.node import Node
from app.service_objects.digital_ocean_node_manager import DigitalOceanNodeManager, DIGITAL_OCEAN_REGIONS

from app.tests.support.fake_digital_ocean_manager import FakeDigitalOceanManager

class TestDigitalOceanNodeManager(TestBase):

    @patch('app.service_objects.digital_ocean_node_manager.Manager')
    def test_rebuild_server_from_latest_snapshot(self, mock_do_manager_class):
        """
        Test that the current droplet is rebuilt from the latest snapshot
        """

        node = Node(provider='digital_ocean', provider_id='droplet123')
        db.session.add(node)
        db.session.commit()

        fake_digital_ocean_manager = FakeDigitalOceanManager(token='asd123')

        mock_do_manager = mock_do_manager_class.return_value
        mock_do_manager.get_droplet_snapshots.return_value = fake_digital_ocean_manager.get_droplet_snapshots()
        mock_do_manager.get_droplet.return_value = fake_digital_ocean_manager.get_droplet()
        mock_droplet = mock_do_manager.get_droplet.return_value

        DigitalOceanNodeManager(node).rebuild_server_from_latest_snapshot()

        mock_do_manager.get_droplet.assert_called_with(node.provider_id)
        # test that provider attributes have been updated from Digital Ocean
        n = Node.query.filter_by(provider_id='droplet123').all()[0]
        self.assertEqual(n.provider_status, 'exploding')

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

    def test_pick_random_region(self):
        """
        Test that it picks a random Digital Ocean region
        """
        node = Node(provider='digital_ocean')

        returned_region = DigitalOceanNodeManager(node)._pick_random_region()
        self.assertTrue(returned_region['name'] in list(map(lambda r: r['name'], DIGITAL_OCEAN_REGIONS)))

        actual_region = list(filter(lambda r: r['name'] == returned_region['name'], DIGITAL_OCEAN_REGIONS))[0]
        self.assertEqual(returned_region['slug'], actual_region['slug'])
