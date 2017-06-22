
import os
import time
import digitalocean

# TODO: change this. import app directly, instead of creating it
from app import create_app
config_name = os.getenv('FLASK_CONFIG') or 'development'
app = create_app(config_name)

from app import db
from .node_manager import NodeManager
from app.models.node import Node

class DigitalOceanNodeManager(NodeManager):
    def __init__(self, node):
        self.manager = digitalocean.Manager(token=app.config['DIGITAL_OCEAN_ACCESS_TOKEN'])
        self.node = node
        return

    def create_droplet_from_template(self):
        """
        Creates a new droplet from the latest template snapshot
        """
        image = self.get_latest_template_snapshot()

        # create new droplet from image
        droplet = digitalocean.Droplet(
            token=app.config['DIGITAL_OCEAN_ACCESS_TOKEN'],
            name = str(self.node.id),
            region='sfo2',
            image=image.id,
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
        db.session.commit()
        self.update_provider_attributes()

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

        db.session.commit()
        return

    def take_snapshot(self):
        """
        Creates a snapshot from the given droplet.
        """
        # TODO: this assumes that the server has already been turned off.
        droplet = self.manager.get_droplet(self.node.provider_id)
        snapshot_name = str(int(time.time()))  # use current utc epoch time as name of the snapshot
        snapshot = droplet.take_snapshot(snapshot_name, return_dict=True, power_off=False)
        return(snapshot)

    def get_latest_template_snapshot(self):
        """
        Gets the latest snapshot object from Digital Ocean
        """
        # find latest snapshot of the template node
        template_node = Node.query.filter_by(provider='digital_ocean', is_template_node=True).first()
        template_droplet = self.manager.get_droplet(template_node.provider_id)

        snapshots = template_droplet.get_snapshots()
        # TODO: pick between snapshots: the latest created_at value
        snapshot = snapshots[1]
        image = self.manager.get_image(snapshot.id)

        return image
