
from unittest.mock import patch
from app.tests.test_base import TestBase
import datetime

from app import db
from app.models.node import Node
from app.service_objects.aws_node_manager import AWSNodeManager

class TestAWSNodeManager(TestBase):

    @patch('app.service_objects.aws_node_manager.boto3')
    def test_update_provider_attributes(self, mock_boto3):
        """
        Test that the node's db attributes are updated to match ones returned by AWS.
        """
        node = Node(provider='aws', name='Node 1', provider_id='random_name')
        db.session.add(node)
        db.session.commit()

        mock_manager = mock_boto3.client.return_value
        mock_manager.get_instance.return_value = {
            'instance': {
                'name': 'random_name',
                'arn': 'arn:aws:lightsail:us-west-2:87016134',
                'supportCode': '560918846632/i-0bce024034136a6f',
                'createdAt': datetime.datetime(2017, 8, 2, 13, 53, 0, 958000),
                'location': {'availabilityZone': 'us-west-2a', 'regionName': 'us-west-2'},
                'resourceType': 'Instance',
                'blueprintId': 'ubuntu_16_04_1',
                'blueprintName': 'Ubuntu',
                'bundleId': 'micro_1_0',
                'isStaticIp': False,
                'privateIpAddress': '172.26.1.133',
                'publicIpAddress': '34.212.143.170',
                'state': {'code': 16, 'name': 'running'},
                'username': 'ubuntu', 'sshKeyName': 'bu_id_rsa'
            }
        }

        AWSNodeManager(node).update_provider_attributes()

        mock_manager.get_instance.assert_called()
        n = Node.query.filter_by(name='Node 1').all()[0]
        self.assertEqual(n.provider_id, 'random_name')
        self.assertEqual(n.provider_status, 'running')
        self.assertEqual(n.ipv4_address, '34.212.143.170')
        self.assertEqual(n.provider_data['privateIpAddress'], '172.26.1.133')

    @patch('app.service_objects.aws_node_manager.boto3')
    def test_destroy_server_successful(self, mock_boto3):
        """
        Test that it destroys the node,
        and returns True when successful
        """
        node = Node(provider='aws', name='Node 1', provider_id='random_name')
        db.session.add(node)
        db.session.commit()

        mock_manager = mock_boto3.client.return_value
        mock_manager.delete_instance.return_value = {
            'operations': [{
                    'id': 'string',
                    'resourceName': 'string',
                    'resourceType': 'Instance',
                    'createdAt': datetime.datetime(2015, 1, 1),
                    'location': {'availabilityZone': 'string', 'regionName': 'us-east-1'},
                    'isTerminal': True,
                    'operationDetails': 'string',
                    'operationType': 'DeleteInstance',
                    'status': 'Succeeded',
                    'statusChangedAt': datetime.datetime(2015, 1, 1),
                    'errorCode': 'string',
                    'errorDetails': 'string'
                }]
        }

        resp = AWSNodeManager(node).destroy_server()
        mock_manager.delete_instance.assert_called_with(instanceName='random_name')
        self.assertEqual(resp, True)

    @patch('app.service_objects.aws_node_manager.boto3')
    def test_destroy_server_unsuccessful(self, mock_boto3):
        """
        Test that it destroys the node,
        and returns False when unsuccessful
        """
        node = Node(provider='aws', name='Node 1', provider_id='random_name')
        db.session.add(node)
        db.session.commit()

        mock_manager = mock_boto3.client.return_value
        mock_manager.delete_instance.return_value = {
            'operations': [{
                    'id': 'string',
                    'resourceName': 'string',
                    'resourceType': 'Instance',
                    'createdAt': datetime.datetime(2015, 1, 1),
                    'location': {'availabilityZone': 'string', 'regionName': 'us-east-1'},
                    'isTerminal': True,
                    'operationDetails': 'string',
                    'operationType': 'DeleteInstance',
                    'status': 'Failed',
                    'statusChangedAt': datetime.datetime(2015, 1, 1),
                    'errorCode': 'string',
                    'errorDetails': 'string'
                }]
        }

        resp = AWSNodeManager(node).destroy_server()
        mock_manager.delete_instance.assert_called_with(instanceName='random_name')
        self.assertEqual(resp, False)

    @patch('app.service_objects.aws_node_manager.boto3')
    def test_power_on(self, mock_boto3):
        """
        Test that it boots up the node.
        """
        node = Node(provider='aws', name='Node 1', provider_id='random_name')
        db.session.add(node)
        db.session.commit()

        mock_manager = mock_boto3.client.return_value

        AWSNodeManager(node).power_on()
        mock_manager.start_instance.assert_called_with(instanceName='random_name')

    @patch('app.service_objects.aws_node_manager.boto3')
    def test_get_latest_snapshot(self, mock_boto3):
        """
        Test that it gets the latest snapshot
        """
        node = Node(provider='aws', name='Node 1', provider_id='random_name')
        db.session.add(node)
        db.session.commit()

        mock_manager = mock_boto3.client.return_value
        mock_manager.get_instance_snapshots.return_value = {
            'instanceSnapshots': [
                {
                    'name': 'snapshot1',
                    'arn': 'string',
                    'supportCode': 'string',
                    'createdAt': datetime.datetime(2015, 1, 1),
                    'location': { 'availabilityZone': 'string', 'regionName': 'us-east-1' },
                    'resourceType': 'InstanceSnapshot',
                    'state': 'available',
                    'progress': 'string',
                    'fromInstanceName': 'string',
                    'fromInstanceArn': 'string',
                    'fromBlueprintId': 'string',
                    'fromBundleId': 'string',
                    'sizeInGb': 123
                },
                {
                    'name': 'snapshot2',
                    'arn': 'string',
                    'supportCode': 'string',
                    'createdAt': datetime.datetime(2016, 1, 1),
                    'location': { 'availabilityZone': 'string', 'regionName': 'us-east-1' },
                    'resourceType': 'InstanceSnapshot',
                    'state': 'available',
                    'progress': 'string',
                    'fromInstanceName': 'string',
                    'fromInstanceArn': 'string',
                    'fromBlueprintId': 'string',
                    'fromBundleId': 'string',
                    'sizeInGb': 123
                }
            ],
            'nextPageToken': 'string'
        }

        returned_snapshot = AWSNodeManager(node).get_latest_snapshot()
        mock_manager.get_instance_snapshots.assert_called()
        self.assertEqual(returned_snapshot['name'], 'snapshot2')

    @patch('app.service_objects.aws_node_manager.boto3')
    def test_create_server_from_latest_snapshot(self, mock_boto3):
        """
        Test that it creates a new instance from the latest template snapshot.
        """
        node = Node(provider='aws', name='Node 1')
        db.session.add(node)
        db.session.commit()

        mock_manager = mock_boto3.client.return_value
        mock_manager.get_instance_snapshots.return_value = {
            'instanceSnapshots': [{
                'name': 'snapshot1',
                'arn': 'string',
                'supportCode': 'string',
                'createdAt': datetime.datetime(2015, 1, 1),
                'location': { 'availabilityZone': 'string', 'regionName': 'us-east-1' },
                'resourceType': 'InstanceSnapshot',
                'state': 'available',
                'progress': 'string',
                'fromInstanceName': 'string',
                'fromInstanceArn': 'string',
                'fromBlueprintId': 'string',
                'fromBundleId': 'string',
                'sizeInGb': 123
            }]
        }
        mock_manager.create_instances_from_snapshot.return_value = {
            'operations': [{
                'id': 'string',
                'resourceName': 'random_node',
                'resourceType': 'Instance',
                'createdAt': datetime.datetime(2015, 1, 1),
                'location': {'availabilityZone': 'string', 'regionName': 'us-east-1'},
                'operationDetails': 'string',
                'operationType': 'CreateInstancesFromSnapshot',
                'status': 'Completed',
                'statusChangedAt': datetime.datetime(2015, 1, 1),
                'errorCode': 'string',
                'errorDetails': 'string'
            }]
        }

        AWSNodeManager(node).create_server_from_latest_snapshot()

        n = Node.query.filter_by(name='Node 1').all()[0]
        self.assertEqual(n.provider_id, 'random_node')

    @patch('app.service_objects.aws_node_manager.boto3')
    def test_create_server(self, mock_boto3):
        """
        Test that it creates a new instance.
        """
        node = Node(provider='aws', name='Node 1')
        db.session.add(node)
        db.session.commit()

        mock_manager = mock_boto3.client.return_value
        mock_manager.create_instances.return_value = {
            'operations': [
                {
                    'id': 'string',
                    'resourceName': 'random_node',
                    'resourceType': 'Instance',
                    'createdAt': datetime.datetime(2015, 1, 1),
                    'location': {'availabilityZone': 'string', 'regionName': 'test-region'},
                    'isTerminal': False,
                    'operationDetails': 'string',
                    'operationType': 'CreateInstance',
                    'status': 'Started',
                    'statusChangedAt': datetime.datetime(2015, 1, 1),
                    'errorCode': 'string',
                    'errorDetails': 'string'
                },
            ]
        }

        AWSNodeManager(node).create_server()
        db.session.refresh(node)
        self.assertEqual(node.provider_id, 'random_node')
        self.assertEqual(node.provider_region, 'test-region')
        self.assertTrue(datetime.datetime.now(datetime.timezone.utc) - node.launched_at < datetime.timedelta(minutes=1))

    @patch('app.service_objects.aws_node_manager.boto3')
    def test_open_bitcoind_port(self, mock_boto3):
        """
        Test that it opens the new network port
        """
        node = Node(provider='aws', name='Node 1', provider_id='test_instance')
        db.session.add(node)
        db.session.commit()

        mock_manager = mock_boto3.client.return_value

        AWSNodeManager(node).open_bitcoind_port()

        mock_manager.open_instance_public_ports.assert_called_with(
            portInfo={'fromPort': 8333, 'toPort': 8333, 'protocol': 'tcp'},
            instanceName='test_instance'
        )

    @patch('app.service_objects.aws_node_manager.random')
    def test_pick_node_region_existing(self, mock_random):
        """
        Test that it returns the node's region, if the node already has a region.
        """
        node = Node(provider='aws', name='Node 1', provider_id='test_instance', provider_region='test-region')
        db.session.add(node)
        db.session.commit()

        returned_region_name = AWSNodeManager(node)._pick_node_region()

        self.assertEqual(returned_region_name, 'test-region')
        mock_random.choice.assert_not_called()

    @patch('app.service_objects.aws_node_manager.random')
    def test_pick_node_region_new(self, mock_random):
        """
        Test that it returns a random region, if the node does not already have a region.
        """
        node = Node(provider='aws', name='Node 1', provider_id='test_instance')
        db.session.add(node)
        db.session.commit()
        mock_random.choice.return_value = { 'displayName': 'Singapore', 'name': 'ap-southeast-1' }

        returned_region_name = AWSNodeManager(node)._pick_node_region()

        self.assertEqual(returned_region_name, 'ap-southeast-1')
        mock_random.choice.assert_called()

    @patch('app.service_objects.aws_node_manager.random')
    def test_pick_availability_zone(self, mock_random):
        """
        Test that it returns an availability zone which matches the region.
        """
        node = Node(provider='aws', name='Node 1', provider_id='test_instance', provider_region='us-east-1')
        db.session.add(node)
        db.session.commit()

        returned_availability_zone = AWSNodeManager(node)._pick_node_availability_zone()

        self.assertEqual(returned_availability_zone, 'us-east-1a')
        mock_random.choice.assert_not_called()
