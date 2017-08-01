
from datetime import datetime, timezone

from sqlalchemy import Column, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import INTEGER, TIMESTAMP, VARCHAR, JSONB, FLOAT
from sqlalchemy import event

from app import db
from app.utils.invoice import create_order_id
from .state_mixin import StateMixin

class Invoice(db.Model, StateMixin):
    __tablename__= 'invoices'

    id = Column(INTEGER, primary_key=True)
    user_id = Column(INTEGER, ForeignKey('users.id'), nullable=False)
    node_id = Column(INTEGER, ForeignKey('nodes.id'), nullable=False)
    order_id = Column(INTEGER, default=create_order_id)
    price = Column(FLOAT, nullable=False)
    currency = Column(VARCHAR, nullable=False, server_default='USD')
    status = Column(VARCHAR, nullable=False, server_default='new')
    bitpay_invoice_created_at = Column(TIMESTAMP(timezone=True))
    bitpay_id = Column(VARCHAR)
    bitpay_data = Column(JSONB)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    user = db.relationship('User', back_populates='invoices')
    node = db.relationship('Node', back_populates='invoice')

    # state machine
    # Refer to Bitpay's invoice states here: https://bitpay.com/docs/invoice-states
    states = [
        'new',  # a new Invoice record created in the DB.
        'generated', # the invoice record has been created on Bitpay.
        'paid', # the User has paid for the invoice
        'confirmed',  # the payment has been confirmed due to our requirements ('slow' means after 6 blocks)
        'complete',  # the payment is complete (i.e. after 6 blocks)
        'expired',  # payment was not received within a 15 minute window, and the invoice expired.
        'invalid'  # invoice was paid, but payment was not confirmed within 1 hour after receipt. Need to contact Bitpay to resolve these, in case they go through later.
    ]
    transitions = [
        { 'trigger': 'generate', 'source': ['new'], 'dest': 'generated', 'conditions': '_generate_on_bitpay' },
        { 'trigger': 'pay', 'source': ['expired', 'invalid', 'generated'], 'dest': 'paid' },
        { 'trigger': 'confirm', 'source': ['expired', 'invalid', 'generated', 'paid'], 'dest': 'confirmed', 'before': '_provision_node' },
        { 'trigger': 'complete', 'source': ['expired', 'invalid', 'generated', 'paid', 'confirmed'], 'dest': 'complete' },
        { 'trigger': 'expire', 'source': ['generated'], 'dest': 'expired' },
        { 'trigger': 'invalidate', 'source': ['paid'], 'dest': 'invalid' }
    ]

    def _generate_on_bitpay(self):
        """
        Generates an invoice on Bitpay
        """
        invoice_created_successfully = BitpayClient().create_invoice_on_bitpay(self)
        return(invoice_created_successfully)

    def _provision_node(self):
        """
        Provisions the node paid for by the invoice.
        """
        self.node.provision()

    def possible_transitions_to(self, dest):
        """
        Returns all possible transitions between the current state as source and the provided dest destination states
        """
        possible_transitions = list(
            filter(
                lambda transition: (self.status in transition['source']) and (dest == transition['dest']),
                self.__class__.transitions
            )
        )
        return(possible_transitions)

    def generated_minutes_ago(self):
        """
        Returns an number specifying how many minutes ago the invoice was generated on Bitpay.
        """
        mins_ago = None

        if self.bitpay_invoice_created_at:
            diff = datetime.now(timezone.utc) - self.bitpay_invoice_created_at
            mins_ago = diff.seconds / 60

        return(mins_ago)

    def __repr__(self):
        return "Bitpay invoice (%r)" % (self.bitpay_id)

# initialize Invoice state machine
event.listen(Invoice, 'init', Invoice.init_state_machine)
event.listen(Invoice, 'load', Invoice.init_state_machine)

from app.service_objects.bitpay_client import BitpayClient
