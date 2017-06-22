"""change_ad_eb_defaults_and_types

Revision ID: 2926052733ea
Revises: acf0ef1eb665
Create Date: 2017-06-22 14:31:21.757012

"""
from alembic import op
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import INTEGER, FLOAT


# revision identifiers, used by Alembic.
revision = '2926052733ea'
down_revision = 'acf0ef1eb665'
branch_labels = None
depends_on = None

def upgrade():
    op.alter_column('nodes', 'bu_ad', server_default='12')
    op.alter_column('nodes', 'bu_eb', type_=FLOAT, server_default='16.00')

def downgrade():
    op.alter_column('nodes', 'bu_eb', type_=INTEGER, server_default='12')
    op.alter_column('nodes', 'bu_ad', server_default='16')
