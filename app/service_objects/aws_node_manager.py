
import os
import time
import random
from datetime import datetime

from flask import current_app
from app import db
from .node_manager import NodeManager

import boto3

# Queried from http://boto3.readthedocs.io/en/latest/reference/services/lightsail.html#Lightsail.Client.get_regions
# Note: the bu_id_rsa.pub public key has been configured in AWS Lightsail for each of these regions.
AWS_REGIONS = [
    { 'displayName': 'Virginia', 'name': 'us-east-1' },
    { 'displayName': 'Ohio', 'name': 'us-east-2' },
    { 'displayName': 'Oregon', 'name': 'us-west-2' },
    { 'displayName': 'Ireland', 'name': 'eu-west-1' },
    { 'displayName': 'London', 'name': 'eu-west-2' },
    { 'displayName': 'Frankfurt', 'name': 'eu-central-1' },
    { 'displayName': 'Singapore', 'name': 'ap-southeast-1' },
    { 'displayName': 'Tokyo', 'name': 'ap-northeast-1' }
]

class AWSNodeManager(NodeManager):
    def __init__(self, node, aws_sdk=boto3):
        self.node = node
        self.region = self._pick_node_region()
        self.manager = boto3.client(
            'lightsail',
            aws_access_key_id=current_app.config['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=current_app.config['AWS_SECRET_ACCESS_KEY'],
            region_name=self.region
        )
        return

    def create_server(self):
        """
        Creates a new instance.
        """
        response = self.manager.create_instances(
            instanceNames=[str(self.node.id)],
            availabilityZone=self._pick_node_availability_zone(),
            blueprintId='ubuntu_16_04_1',
            bundleId='micro_1_0',
            keyPairName='bu_id_rsa'
        )
        instance = response['operations'][0]
        self.node.provider_id = instance['resourceName']
        self.node.provider_region = instance['location']['regionName']
        self.node.launched_at = datetime.utcnow()
        db.session.add(self.node)
        db.session.commit()

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

    def open_bitcoind_port(self):
        """
        Opens TCP port 8333 on the machine
        """
        tcp_port_number=8333
        self.manager.open_instance_public_ports(
            portInfo={'fromPort': tcp_port_number, 'toPort': tcp_port_number, 'protocol': 'tcp'},
            instanceName=self.node.provider_id
        )

    def destroy_server(self):
        """
        Destroys the node
        """
        # TODO: check that this actually returns true / false as I think
        resp = self.manager.delete_instance(instanceName=self.node.provider_id)

        status = resp['operations'][0]['status']
        if status == 'Succeeded':
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

    def create_server_from_latest_snapshot(self):
        """
        Creates a new instance from the latest template snapshot
        """
        snapshot = self.get_latest_snapshot()

        response = self.manager.create_instances_from_snapshot(
            instanceNames=[str(self.node.id)],
            availabilityZone=self._pick_node_availability_zone(),
            instanceSnapshotName=snapshot['name'],
            bundleId='micro_1_0',
        )
        instance = response['operations'][0]

        # update node's values in the db
        self.node.provider_id = instance['resourceName']
        self.node.launched_at = datetime.utcnow()
        db.session.add(self.node)
        db.session.commit()

    def _pick_node_region(self):
        """
        If the node already has a region, it returns that.
        Else, it picks a random region for the node.
        """
        if self.node.provider_region:
            return(self.node.provider_region)
        else:
            region = random.choice(AWS_REGIONS)
            return(region['name'])

    def _pick_node_availability_zone(self):
        """
        Returns an availability zone that matches with the node's region.
        """
        # for simplicity, pick the first availability zone in the region.
        return(self.region + 'a')
