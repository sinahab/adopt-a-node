
import os
import time
from datetime import datetime

from flask import current_app
from app import db
from .node_manager import NodeManager

import boto3

class AWSNodeManager(NodeManager):
    def __init__(self, node, aws_sdk=boto3):
        self.node = node
        self.manager = boto3.client(
            'ec2',
            aws_access_key_id=current_app.config['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=current_app.config['AWS_SECRET_ACCESS_KEY'],
            region_name='us-west-2'
        )
        return

    def create_server_from_latest_snapshot(self):
        """
        Creates a new instance from the latest template snapshot
        """
        snapshot = self.get_latest_snapshot()

        response = self.manager.run_instances(
            BlockDeviceMappings=[{'DeviceName': '/dev/sda1', 'Ebs': {'VolumeSize': 40, 'VolumeType': 'gp2'}}],
            ImageId=snapshot['ImageId'],
            InstanceType='t2.micro',
            KeyName='bu-keypair-uswest2',
            MaxCount=1,
            MinCount=1,
            Monitoring={ 'Enabled': False },
            NetworkInterfaces=[
                {
                    'DeviceIndex': 0,
                    'SubnetId': 'subnet-0b33196c',
                    'AssociatePublicIpAddress': True,
                    'Groups': [ 'sg-841e33ff' ]
                },
            ]
        )
        instance = response['Instances'][0]

        # update node's values in the db
        self.node.provider_id = instance['InstanceId']
        db.session.add(self.node)
        db.session.commit()


    def get_latest_snapshot(self):
        """
        Gets the latest available image object from AWS
        """
        response = self.manager.describe_images(
            Filters=[{ 'Name': 'owner-id', 'Values': [current_app.config['AWS_ACCOUNT_ID']] }]
        )

        images = response['Images']
        available_images = list(filter(lambda i: i['State'] == 'available', images))
        latest_available_image = max(available_images, key=lambda i: datetime.strptime(i['CreationDate'], '%Y-%m-%dT%H:%M:%S.%fZ'))

        return(latest_available_image)

    def power_on(self):
        """
        Boots up the node
        """
        self.manager.start_instances(
            InstanceIds=[self.node.provider_id]
        )

    def take_snapshot(self):
        """
        Creates a snapshot from the given node.
        """
        image_name = str(int(time.time()))
        image = self.manager.create_image(InstanceId=self.node.provider_id, Name=image_name)
        return(image)

    def update_provider_attributes(self):
        """
        Queries AWS and updates the node's data in the db accordingly
        """
        instance = self.get_instance()

        # drop unnecessary or hard-to-save data
        instance.pop('LaunchTime', None)
        instance.pop('BlockDeviceMappings', None)
        instance.pop('NetworkInterfaces', None)
        instance.pop('PrivateIpAddresses', None)

        self.node.ipv4_address = instance['PublicIpAddress']
        self.node.provider_status = instance['State']['Name']
        self.node.provider_data = instance

        db.session.add(self.node)
        db.session.commit()
        return(instance)

    def get_instance(self):
        """
        Queries AWS for the node's associated instance
        """
        response = self.manager.describe_instances(
            InstanceIds=[self.node.provider_id]
        )

        instances = response['Reservations'][0]['Instances']
        return(instances[0])
