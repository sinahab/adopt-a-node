"""create nodes table

Revision ID: 184bd8f97f79
Revises: 183c42742a0e
Create Date: 2017-06-14 15:33:42.253727

"""
from alembic import op
from sqlalchemy import Column, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import INTEGER, TIMESTAMP, VARCHAR, BOOLEAN

# revision identifiers, used by Alembic.
revision = '184bd8f97f79'
down_revision = '183c42742a0e'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'nodes',
        Column('id', INTEGER, primary_key=True),
        Column('user_id', INTEGER, ForeignKey('users.id')),

        Column('provider', VARCHAR, nullable=False),
        Column('ipv4_address', VARCHAR, nullable=False),

        Column('bu_ad', INTEGER, nullable=False, server_default='16'),
        Column('bu_eb', INTEGER, nullable=False, server_default='12'),
        Column('name', VARCHAR),

        Column('bu_version', VARCHAR),
        Column('status', VARCHAR, nullable=False, server_default='initializing'),
        Column('expiration_date', TIMESTAMP(timezone=True)),

        Column('created_at', TIMESTAMP(timezone=True), nullable=False, server_default=func.now()),
        Column('updated_at', TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    )

    op.create_index('unique_nodes_ipv4', 'nodes', ['ipv4_address'], unique=True)
    op.create_index('index_nodes_on_provider', 'nodes', ['provider'])
    op.create_index('index_nodes_on_status', 'nodes', ['status'])
    op.create_index('index_nodes_on_expiration_date', 'nodes', ['expiration_date'])

def downgrade():
    op.drop_table('nodes')
