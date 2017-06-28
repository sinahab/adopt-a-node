"""create invoices table

Revision ID: 1c341a5fccb8
Revises: f5821a84b724
Create Date: 2017-06-28 11:59:16.111435

"""
from alembic import op
from sqlalchemy import Column, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import INTEGER, TIMESTAMP, VARCHAR, BOOLEAN, FLOAT, JSONB

# revision identifiers, used by Alembic.
revision = '1c341a5fccb8'
down_revision = 'f5821a84b724'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'invoices',
        Column('id', INTEGER, primary_key=True),
        Column('user_id', INTEGER, ForeignKey('users.id'), nullable=False),
        Column('node_id', INTEGER, ForeignKey('nodes.id'), nullable=False),

        Column('order_id', INTEGER),
        Column('price', FLOAT, nullable=False),
        Column('currency', VARCHAR, nullable=False, server_default='USD'),
        Column('status', VARCHAR, nullable=False, server_default='new'),

        Column('bitpay_invoice_created_at', TIMESTAMP(timezone=True)),
        Column('bitpay_id', INTEGER),
        Column('bitpay_data', JSONB),

        Column('created_at', TIMESTAMP(timezone=True), nullable=False, server_default=func.now()),
        Column('updated_at', TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    )

    op.create_index('unique_invoices_order_id', 'invoices', ['order_id'], unique=True)
    op.create_index('unique_invoices_bitpay_id', 'invoices', ['bitpay_id'], unique=True)
    op.create_index('index_invoices_on_status', 'invoices', ['status'])
    op.create_index('index_invoices_on_user_id', 'invoices', ['user_id'])
    op.create_index('index_invoices_on_node_id', 'invoices', ['node_id'])

def downgrade():
    op.drop_table('invoices')
