"""remove_nullable_from_nodes_ip

Revision ID: 8004099d48dc
Revises: 184bd8f97f79
Create Date: 2017-06-19 14:28:02.071020

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = '8004099d48dc'
down_revision = '184bd8f97f79'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('nodes', 'ipv4_address', nullable=True)

def downgrade():
    op.alter_column('nodes', 'ipv4_address', nullable=False)
