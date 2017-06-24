
from sqlalchemy import Column, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import INTEGER, TIMESTAMP, VARCHAR, JSONB, BOOLEAN
from sqlalchemy.orm import validates
from sqlalchemy import event

from app import db
from .state_mixin import StateMixin

class Node(db.Model, StateMixin):
    __tablename__= 'nodes'

    id = Column(INTEGER, primary_key=True)
    user_id = Column(INTEGER, ForeignKey('users.id'))
    provider = Column(VARCHAR, nullable=False)
    ipv4_address = Column(VARCHAR)
    bu_ad = Column(INTEGER, nullable=False, server_default='16')
    bu_eb = Column(INTEGER, nullable=False, server_default='12')
    name = Column(VARCHAR)
    bu_version = Column(VARCHAR)
    status = Column(VARCHAR, nullable=False, server_default='new')
    expiration_date = Column(TIMESTAMP(timezone=True))
    provider_id = Column(INTEGER)
    provider_status = Column(VARCHAR)
    provider_data = Column(JSONB)
    is_template_node = Column(BOOLEAN, server_default='False')
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    user = db.relationship('User', back_populates='nodes')

    # state machine
    states = ['new','provisioned', 'configured', 'up']
    transitions = [
        { 'trigger': 'provision', 'source': 'new', 'dest': 'provisioned', 'before': '_provision_node'},
        { 'trigger': 'configure', 'source': 'provisioned', 'dest': 'configured', 'before': '_configure_node', 'after': 'start'},
        { 'trigger': 'start', 'source': 'configured', 'dest': 'up', 'before': '_start_node'}
    ]

    def _provision_node(self):
        """
        Provisions a server on the given cloud provider.
        Also, schedules the node for configuration.
        This needs to happen after a delay, so that provisioning is already complete.
        """
        DigitalOceanNodeManager(self).create_droplet_from_latest_snapshot()
        configure_node.apply_async(args=(self.id,), countdown=2700)
        return

    def _configure_node(self):
        """
        Configures the bitcoind client to have the provided attributes (EB, AD, and subVersion).
        """
        DigitalOceanNodeManager(self).update_bitcoin_conf()
        return

    def _start_node(self):
        """
        Starts the bitcoind client on the node.
        """
        DigitalOceanNodeManager(self).restart_bitcoind()
        return

    @validates('provider')
    def validate_email(self, key, provider):
        assert provider in ('aws', 'digital_ocean')
        return provider

    def __repr__(self):
        return "IPv4 Address(%r)" % (self.ipv4_address)

# initialize node state machine
event.listen(Node, 'init', Node.init_state_machine)
event.listen(Node, 'load', Node.init_state_machine)

from app.service_objects.digital_ocean_node_manager import DigitalOceanNodeManager
from app.tasks import configure_node
from .user import User
