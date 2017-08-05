
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
            'lightsail',
            aws_access_key_id=current_app.config['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=current_app.config['AWS_SECRET_ACCESS_KEY'],
            region_name='us-west-2'
        )
        return

    def update_provider_attributes(self):
        """
        Queries AWS and updates the node's data in the db accordingly
        """
        instance = self.manager.get_instance(instanceName=self.node.provider_id)
        instance = instance['instance']

        instance.pop('createdAt', None)
        self.node.ipv4_address = instance['publicIpAddress']
        self.node.provider_status = instance['state']['name']
        self.node.provider_data = instance

        db.session.add(self.node)
        db.session.commit()
        return

    def destroy_node(self):
        """
        Destroys the node
        """
        # TODO: check that this actually returns true / false as I think
        resp = self.manager.delete_instance(instanceName=self.node.provider_id)

        status = resp['operations'][0]['status']
        if status == 'Completed':
            return(True)
        else:
            return(False)

    def power_on(self):
        """
        Boots up the node
        """
        self.manager.start_instance(instanceName=self.node.provider_id)

    def get_latest_snapshot(self):
        """
        Gets the latest available image object from AWS
        """
        response = self.manager.get_instance_snapshots()

        snapshots = response['instanceSnapshots']
        available_snapshots = list(filter(lambda s: s['state'] == 'available', snapshots))
        latest_available_snapshot = max(available_snapshots, key=lambda i: i['createdAt'])

        return(latest_available_snapshot)

    def take_snapshot(self):
        """
        Creates a snapshot from the given node.
        """
        snapshot_name = str(int(time.time()))
        snapshot = self.manager.create_instance_snapshot(instanceName=self.node.provider_id, instanceSnapshotName=snapshot_name)
        return(snapshot)


    def create_server_from_latest_snapshot(self):
        """
        Creates a new instance from the latest template snapshot
        """
        snapshot = self.get_latest_snapshot()

        response = self.manager.create_instances_from_snapshot(
            instanceNames=[str(self.node.id)],
            availabilityZone='us-west-2',
            instanceSnapshotName=snapshot['name'],
            bundleId='nano_1_0',
        )
        instance = response['operations'][0]

        # update node's values in the db
        self.node.provider_id = instance['resourceName']
        db.session.add(self.node)
        db.session.commit()
