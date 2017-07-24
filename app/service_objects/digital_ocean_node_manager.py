
import os
import random
import time
from digitalocean import Manager, Droplet
from datetime import datetime
from flask import current_app

from app import db
from .node_manager import NodeManager

# Queried from https://developers.digitalocean.com/documentation/v2/#list-all-regions
DIGITAL_OCEAN_REGIONS = [
    { 'slug': 'sfo1', 'name': 'San Francisco 1' },
    { 'slug': 'sfo2', 'name': 'San Francisco 2' },
    { 'slug': 'nyc1', 'name': 'New York 1' },
    { 'slug': 'nyc3', 'name': 'New York 3' },
    { 'slug': 'ams2', 'name': 'Amsterdam 2' },
    { 'slug': 'ams3', 'name': 'Amsterdam 3' },
    { 'slug': 'sgp1', 'name': 'Singapore 1' },
    { 'slug': 'lon1', 'name': 'London 1' },
    { 'slug': 'fra1', 'name': 'Frankfurt 1' },
    { 'slug': 'tor1', 'name': 'Toronto 1' },
    { 'slug': 'blr1', 'name': 'Bangalore 1' }
]

class DigitalOceanNodeManager(NodeManager):
    def __init__(self, node):
        self.manager = Manager(token=current_app.config['DIGITAL_OCEAN_ACCESS_TOKEN'])
        self.node = node
        return

    def create_server_from_latest_snapshot(self):
        """
        Creates a new droplet from the latest template snapshot
        """
        snapshot = self.get_latest_snapshot()

        # create new droplet from snapshot
        droplet = Droplet(
            token=current_app.config['DIGITAL_OCEAN_ACCESS_TOKEN'],
            name = str(self.node.id),
            region=self._pick_random_region()['slug'],
            image=snapshot.id,
            size_slug='1gb',
            ssh_keys= [9581853],
            backups=False,
            ipv6= False,
            private_networking= False,
            monitoring=False
        )
        droplet.create()

        # update node's values in the db
        self.node.provider_id = droplet.id
        db.session.add(self.node)
        db.session.commit()

        self.update_provider_attributes()

        return

    def rebuild_server_from_latest_snapshot(self):
        """
        Rebuilds the current droplet from the latest snapshot
        """
        snapshot = self.get_latest_snapshot()
        droplet = self.manager.get_droplet(self.node.provider_id)
        droplet.rebuild(image_id=snapshot.id)

        return

    def update_provider_attributes(self):
        """
        Queries Digital Ocean and updates the node's data in the db accordingly
        """
        droplet = self.manager.get_droplet(self.node.provider_id)

        droplet.__dict__.pop('_log', None)
        self.node.ipv4_address = droplet.ip_address
        self.node.provider_status = droplet.status
        self.node.provider_data = droplet.__dict__

        db.session.add(self.node)
        db.session.commit()
        return

    def take_snapshot(self):
        """
        Creates a snapshot from the given droplet.
        """
        droplet = self.manager.get_droplet(self.node.provider_id)
        snapshot_name = str(int(time.time()))  # use current utc epoch time as name of the snapshot
        snapshot = droplet.take_snapshot(snapshot_name, return_dict=True, power_off=False)
        return(snapshot)

    def power_on(self):
        """
        Boots up the node
        """
        droplet = self.manager.get_droplet(self.node.provider_id)
        droplet.power_on(return_dict=True)
        return

    def get_latest_snapshot(self):
        """
        Gets the latest snapshot object from Digital Ocean
        """
        snapshots = self.manager.get_droplet_snapshots()
        latest_snapshot = max(snapshots, key=lambda snapshot: datetime.strptime(snapshot.created_at, '%Y-%m-%dT%H:%M:%SZ'))
        return(latest_snapshot)

    def _pick_random_region(self):
        """
        Picks a random Digital Ocean region to spin up the node
        """
        return(random.choice(DIGITAL_OCEAN_REGIONS))
