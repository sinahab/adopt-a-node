
from .test_base import TestBase

from app.models.node import Node
from app.service_objects.aws_node_manager import AWSNodeManager, boto3

from app.tests.lib.fake_aws_client import FakeAwsClient

# setup test doubles
setattr(boto3, 'client', FakeAwsClient)

class TestAWSNodeManager(TestBase):
    def test_get_latest_snapshot(self):
        """
        Test that returns the latest image object from AWS
        """

        node = Node(provider='aws')
        manager = AWSNodeManager(node, aws_sdk=boto3)
        snapshot = manager.get_latest_snapshot()

        # value returned by FakeAwsClient
        self.assertEqual(snapshot['ImageId'], 'ami-test2')

    def test_create_droplet_from_latest_snapshot(self):
        """
        Creates a new droplet from the latest template snapshot
        """
        node = Node(provider='aws')
        manager = AWSNodeManager(node, aws_sdk=boto3)
        manager.create_droplet_from_latest_snapshot()

        # value returned by FakeAwsClient
        self.assertEqual(node.provider_id, 'i-test123')

    def test_get_instance(self):
        """
        Queries AWS for the node's associated instance
        """
        node = Node(provider='aws')
        manager = AWSNodeManager(node, aws_sdk=boto3)
        instance = manager.get_instance()

        # value returned by FakeAwsClient
        self.assertEqual(instance['InstanceId'], 'i-test-instance')
