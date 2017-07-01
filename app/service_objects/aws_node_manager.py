
import os
from datetime import datetime

from flask import current_app
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

    def get_latest_snapshot(self):
        """
        Gets the latest available image object from AWS
        """
        images = self.manager.describe_images(
            Filters=[{ 'Name': 'owner-id', 'Values': [current_app.config['AWS_ACCOUNT_ID']] }]
        )

        images = images['Images']
        available_images = list(filter(lambda i: i['State'] == 'available', images))
        latest_available_image = max(available_images, key=lambda i: datetime.strptime(i['CreationDate'], '%Y-%m-%dT%H:%M:%S.%fZ'))
        return(latest_available_image)


    def create_droplet_from_latest_snapshot(self):
        pass

    def power_on(self):
        pass

    def take_snapshot(self):
        pass

    def update_provider_attributes(self):
        pass
