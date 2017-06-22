"""add provider specific columns to nodes

Revision ID: acf0ef1eb665
Revises: 8004099d48dc
Create Date: 2017-06-20 19:19:19.763583

"""
from alembic import op
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import INTEGER, VARCHAR, JSONB, BOOLEAN


# revision identifiers, used by Alembic.
revision = 'acf0ef1eb665'
down_revision = '8004099d48dc'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('nodes', Column('provider_id', INTEGER))
    op.add_column('nodes', Column('provider_status', VARCHAR))
    op.add_column('nodes', Column('provider_data', JSONB))
    op.add_column('nodes', Column('is_template_node', BOOLEAN, server_default='False'))

    op.create_index('index_nodes_on_provider_id', 'nodes', ['provider_id'])

def downgrade():
    op.drop_column('nodes', 'provider_id')
    op.drop_column('nodes', 'provider_status')
    op.drop_column('nodes', 'provider_data')
