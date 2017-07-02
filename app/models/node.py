
from sqlalchemy import Column, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import INTEGER, TIMESTAMP, VARCHAR, JSONB, BOOLEAN
from sqlalchemy.orm import validates
from sqlalchemy import event

from datetime import datetime

from app import db
from .state_mixin import StateMixin
from app.service_objects.digital_ocean_node_manager import DigitalOceanNodeManager
from app.service_objects.aws_node_manager import AWSNodeManager

CLOUD_PROVIDERS = ('aws', 'digital_ocean')

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
    launched_at = Column(TIMESTAMP(timezone=True))
    months_adopted = Column(INTEGER)
    provider_id = Column(VARCHAR)
    provider_status = Column(VARCHAR)
    provider_data = Column(JSONB)
    is_template_node = Column(BOOLEAN, server_default='False')
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    user = db.relationship('User', back_populates='nodes')
    invoice = db.relationship('Invoice', uselist=False, back_populates='node')

    # state machine
    states = [
        'new',  # a new node db record, with no associated remote object on a cloud provider.
        'provisioned',  # a remote server has been spun up, on one of the cloud providers
        'configured',   # bitcoin.conf has been updated to the user's desired values.
        'up',  # BU daemon is running.
        'on',   # the server is on, but the BU daemon is not running
        'off',  # the server is powered off
        'taking_snapshot',  # a snapshot of the server is currently being taken.
        'updating_client'   # the BU client on server is being updated.
    ]
    transitions = [
        { 'trigger': 'provision', 'source': 'new', 'dest': 'provisioned', 'before': '_provision'},  # provision a server on the desired cloud provider
        { 'trigger': 'configure', 'source': ['provisioned', 'on'], 'dest': 'configured', 'before': '_configure', 'after': 'start_client'},  # configure bitcoin.conf according to the user's desired values.
        { 'trigger': 'start_client', 'source': ['configured', 'on'], 'dest': 'up', 'before': '_start_client'},  # start the BU daemon
        { 'trigger': 'stop_client', 'source': 'up', 'dest': 'on', 'before': '_stop_client'},  # stop the BU daemon
        { 'trigger': 'power_off', 'source': 'on', 'dest': 'off', 'before': '_power_off'},  # power off the associated server
        { 'trigger': 'power_on', 'source': 'off', 'dest': 'up', 'before': '_power_on'},  # power on the associated server. BU daemon starts automatically, hence 'up' dest.
        { 'trigger': 'begin_taking_snapshot', 'source': 'off', 'dest': 'taking_snapshot', 'before': '_take_snapshot'},  # begin taking a snapshot of the server
        { 'trigger': 'finish_taking_snapshot', 'source': 'taking_snapshot', 'dest': 'off'},  # finish taking a snapshot of the server

        # TODO: implement these
        { 'trigger': 'begin_updating_client', 'source': 'on', 'dest': 'updating_client'},  # begin updating BU client on the server
        { 'trigger': 'finish_updating_client', 'source': 'updating_client', 'dest': 'on'},  # finish updating BU client on the server
    ]

    def _provision(self):
        """
        Provisions a server on the given cloud provider.
        Also, schedules the node for configuration.
        This needs to happen after a delay, so that provisioning is already complete.
        """
        try:
            self.node_manager().create_server_from_latest_snapshot()

            self.launched_at = datetime.utcnow()
            db.session.add(self)
            db.session.commit()

            configure_node.apply_async(args=(self.id,), countdown=2700)
        except Exception as e:
            print(e)

        return

    def _configure(self):
        """
        Configures the BU client to have the provided attributes (EB, AD, and subVersion).
        """
        self.node_manager().update_bitcoin_conf()
        return

    def _start_client(self):
        """
        Starts the BU client on the server.
        """
        self.node_manager().restart_bitcoind()
        return

    def _stop_client(self):
        """
        Stops the BU client on the server.
        """
        self.node_manager().stop_bitcoind()
        return

    def _power_off(self):
        """
        Powers off the server.
        """
        self.node_manager().power_off()
        return

    def _power_on(self):
        """
        Powers on the server.
        """
        self.node_manager().power_on()
        return

    def _take_snapshot(self):
        """
        Takes a snapshot of the server
        """
        self.node_manager().take_snapshot()
        # TODO: schedule job to check if taking snapshot has been completed, and if so, to make the 'finish_taking_snapshot' transition.
        return

    def node_manager(self):
        if self.provider == 'aws':
            return(AWSNodeManager(self))
        elif self.provider == 'digital_ocean':
            return(DigitalOceanNodeManager(self))
        else:
            raise Exception('No supported NodeManager could be found.')

    @validates('provider')
    def validate_email(self, key, provider):
        assert provider in CLOUD_PROVIDERS
        return provider

    def __repr__(self):
        return "IPv4 Address(%r)" % (self.ipv4_address)

# initialize node state machine
event.listen(Node, 'init', Node.init_state_machine)
event.listen(Node, 'load', Node.init_state_machine)

from app.tasks import configure_node
from .user import User
