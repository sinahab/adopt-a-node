
from sqlalchemy import Column, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import INTEGER, TIMESTAMP, VARCHAR, JSONB, FLOAT
from sqlalchemy import event

from app import db
from app.bitpay.utils import create_order_id
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
    bitpay_id = Column(INTEGER)
    bitpay_data = Column(JSONB)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    user = db.relationship('User', back_populates='invoices')
    node = db.relationship('Node', back_populates='invoices')

    # state machine
    states = ['new', 'paid', 'confirmed', 'complete']
    transitions = [
        { 'trigger': 'pay', 'source': 'new', 'dest': 'paid' },
        { 'trigger': 'confirm', 'source': 'paid', 'dest': 'confirmed' },
        { 'trigger': 'complete', 'source': 'confirmed', 'dest': 'complete' }
    ]

    def __repr__(self):
        return "Bitpay invoice (%r)" % (self.bitpay_id)

# initialize Invoice state machine
event.listen(Invoice, 'init', Invoice.init_state_machine)
event.listen(Invoice, 'load', Invoice.init_state_machine)
