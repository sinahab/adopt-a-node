"""change_nodes_status_default

Revision ID: f5821a84b724
Revises: 2926052733ea
Create Date: 2017-06-22 17:46:16.072724

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f5821a84b724'
down_revision = '2926052733ea'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('nodes', 'status', server_default='new')

def downgrade():
    op.alter_column('nodes', 'status', server_default='initializing')
