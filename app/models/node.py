
from flask import current_app
from sqlalchemy import Column, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import INTEGER, TIMESTAMP, VARCHAR, JSONB, BOOLEAN
from sqlalchemy.orm import validates
from sqlalchemy import event

from datetime import datetime
from dateutil.relativedelta import relativedelta
import pytz

from app import db
from .state_mixin import StateMixin
from app.service_objects.digital_ocean_node_manager import DigitalOceanNodeManager
from app.service_objects.aws_node_manager import AWSNodeManager

CLOUD_PROVIDERS = ('aws', 'digital_ocean')
BU_VERSION = '1.0.3'

class Node(db.Model, StateMixin):
    __tablename__= 'nodes'

    id = Column(INTEGER, primary_key=True)
    user_id = Column(INTEGER, ForeignKey('users.id'))
    provider = Column(VARCHAR, nullable=False)
    ipv4_address = Column(VARCHAR)
    bu_ad = Column(INTEGER, nullable=False, server_default='16')
    bu_eb = Column(INTEGER, nullable=False, server_default='12')
    name = Column(VARCHAR)
    bu_version = Column(VARCHAR, default=BU_VERSION)
    status = Column(VARCHAR, nullable=False, server_default='new')
    launched_at = Column(TIMESTAMP(timezone=True))
    months_adopted = Column(INTEGER)
    provider_id = Column(VARCHAR)
    provider_region = Column(VARCHAR)
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
        'installed',  # bitcoind has been installed on the server
        'configured',   # bitcoind ports are open, and bitcoin.conf has been updated to the user's desired values.
        'up',  # bitcoind is running.
        'on',   # the server is on, but the bitcoind is not running
        'off',  # the server is powered off
        'taking_snapshot',  # a snapshot of the server is currently being taken.
        'updating_client',   # bitcoind is being updated.
        'expired'   # the node is no longer provisioned (its adoption period ended)
    ]

    transitions = [
        { 'trigger': 'provision', 'source': 'new', 'dest': 'provisioned', 'before': '_provision'},  # provision a server on the desired cloud provider
        { 'trigger': 'install', 'source': 'provisioned', 'dest': 'installed', 'before': '_install'},  # install bitcoind on the server
        { 'trigger': 'configure', 'source': ['installed', 'on', 'up'], 'dest': 'configured', 'before': '_configure', 'after': 'start_bitcoind'},  # configure bitcoin.conf according to the user's desired values.
        { 'trigger': 'start_bitcoind', 'source': ['configured', 'on'], 'dest': 'up', 'before': '_start_bitcoind'},  # start the BU daemon
        { 'trigger': 'stop_bitcoind', 'source': 'up', 'dest': 'on', 'before': '_stop_bitcoind'},  # stop the BU daemon
        { 'trigger': 'power_off', 'source': 'on', 'dest': 'off', 'before': '_power_off'},  # power off the associated server
        { 'trigger': 'power_on', 'source': 'off', 'dest': 'up', 'before': '_power_on'},  # power on the associated server. BU daemon starts automatically, hence 'up' dest.
        { 'trigger': 'begin_taking_snapshot', 'source': 'off', 'dest': 'taking_snapshot', 'before': '_take_snapshot'},  # begin taking a snapshot of the server
        { 'trigger': 'finish_taking_snapshot', 'source': 'taking_snapshot', 'dest': 'off'},  # finish taking a snapshot of the server
        { 'trigger': 'rebuild', 'source': 'off', 'dest': 'provisioned', 'before': '_rebuild' },  # rebuild server from latest snapshot
        { 'trigger': 'expire', 'source': ['up', 'on', 'off'], 'dest': 'expired', 'conditions': '_expire' }  # expire node
    ]

    def _provision(self):
        """
        Provisions a server on the given cloud provider.
        Also, schedules for bitcoind to be installed on the machine.
        This needs to happen after a delay, so that provisioning is already complete.
        """
        try:
            if self.provider_id:
                raise Exception("Error: node is already associated with a server.")

            self.node_manager().create_server()
            db.session.refresh(self)
            install_bitcoind.apply_async(args=(self.id,), countdown=120)

        except Exception as e:
            current_app.logger.error(e)

        return

    def _install(self):
        """
        Installs bitcoind on the machine, and opens port 8333 on the machine.
        Also, schedules for bitcoind to be configured.
        This needs to happen after a delay, so that provisioning is already complete.
        """
        db.session.expire_on_commit = False
        self.update_provider_attributes()
        self.node_manager().install_bitcoind()
        self.node_manager().open_bitcoind_port()
        configure_node.apply_async(args=(self.id,), countdown=1800)

    def _expire(self):
        """
        Expires the node & deletes the node on cloud provider.
        """
        res = self.node_manager().destroy_server()

        self.provider_status = 'expired_by_adoptanode'
        db.session.add(self)
        db.session.commit()

        return(res)

    def _rebuild(self):
        """
        Rebuilds the existing server from the latest snapshot.
        Also, schedules the node for configuration.
        This needs to happen after a delay, so that provisioning is already complete.
        """
        try:
            self.node_manager().rebuild_server_from_latest_snapshot()

            self.bu_version = BU_VERSION
            db.session.commit()

            configure_node.apply_async(args=(self.id,), countdown=1800)
        except Exception as e:
            current_app.logger.error(e)

    def _configure(self):
        """
        Configures the BU client to have the provided attributes (EB, AD, and subVersion).
        """
        self.node_manager().update_bitcoin_conf()
        return

    def _start_bitcoind(self):
        """
        Starts the BU client on the server.
        """
        self.node_manager().restart_bitcoind()
        return

    def _stop_bitcoind(self):
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

    def update_provider_attributes(self):
        """
        Udates the provider attributes for the node.
        """
        self.node_manager().update_provider_attributes()
        return

    def node_manager(self):
        """
        Returns the appropriate NodeManager for the node, according to it's provider.
        """
        if self.provider == 'aws':
            return(AWSNodeManager(self))
        elif self.provider == 'digital_ocean':
            return(DigitalOceanNodeManager(self))
        else:
            raise Exception('No supported NodeManager could be found.')

    def expires_at(self):
        """
        Returns the datetime at which the node expires.
        """
        expires_at = None

        if self.launched_at:
            expires_at = self.launched_at + relativedelta(months=self.months_adopted)

        return(expires_at)

    def has_expired(self):
        """
        Returns a boolean; is the node expired or not?
        """
        if self.launched_at:
            now = datetime.utcnow().replace(tzinfo=pytz.timezone('utc'))
            return(self.expires_at() < now)
        else:
            return(False)

    @validates('provider')
    def validate_provider(self, key, provider):
        assert provider in CLOUD_PROVIDERS
        return provider

    def __repr__(self):
        return "IPv4 Address(%r)" % (self.ipv4_address)

# initialize node state machine
event.listen(Node, 'init', Node.init_state_machine)
event.listen(Node, 'load', Node.init_state_machine)

from app.tasks import configure_node, install_bitcoind
from .user import User
