"""add_region_to_nodes

Revision ID: 28a22a4ccb7b
Revises: 5bd5513c9eea
Create Date: 2017-08-09 12:57:01.241848

"""
from alembic import op
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import VARCHAR

# revision identifiers, used by Alembic.
revision = '28a22a4ccb7b'
down_revision = '5bd5513c9eea'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('nodes', Column('provider_region', VARCHAR))
    op.create_index('index_nodes_on_provider_region', 'nodes', ['provider_region'])

def downgrade():
    op.drop_column('nodes', 'provider_region')
