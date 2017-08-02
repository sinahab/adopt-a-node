
from app.tests.test_base import TestBase

from app import db
from app.models.node import Node
from app.service_objects.aws_node_manager import AWSNodeManager, boto3

from app.tests.support.fake_aws_client import FakeAwsClient

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

    def test_create_server_from_latest_snapshot(self):
        """
        Tests that an AWS instance is created for the node.
        """
        node = Node(provider='aws')
        manager = AWSNodeManager(node, aws_sdk=boto3)
        manager.create_server_from_latest_snapshot()

        # value returned by FakeAwsClient
        self.assertEqual(node.provider_id, 'i-test123')

    def test_update_provider_attributes(self):
        """
        Test that the node's db attributes are updated to match ones returned by AWS.
        """
        node = Node(provider='aws', provider_status='pending')
        db.session.add(node)
        db.session.commit()

        manager = AWSNodeManager(node, aws_sdk=boto3)
        manager.update_provider_attributes()

        # values returned by FakeAwsClient
        self.assertEqual(node.provider_status, 'stopped')
        self.assertEqual(node.ipv4_address, '12.123.123.12')
        self.assertEqual(node.provider_data['InstanceType'], 't2.micro')

    def test_get_instance(self):
        """
        That that AWS SDK is called with the correct query.
        """
        node = Node(provider='aws', provider_id='123test')
        manager = AWSNodeManager(node, aws_sdk=boto3)
        instance = manager.get_instance()

        # value returned by FakeAwsClient
        self.assertEqual(instance['InstanceId'], 'i-test-instance')
