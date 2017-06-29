"""modify_expiration_on_nodes

Revision ID: a237254c6f5a
Revises: 1c341a5fccb8
Create Date: 2017-06-28 22:58:01.481428

"""
from alembic import op
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import INTEGER, TIMESTAMP, VARCHAR


# revision identifiers, used by Alembic.
revision = 'a237254c6f5a'
down_revision = '1c341a5fccb8'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('nodes', Column('launched_at', TIMESTAMP(timezone=True)))
    op.drop_column('nodes', 'expiration_date')
    op.add_column('nodes', Column('months_adopted', INTEGER))

def downgrade():
    op.drop_column('nodes', 'months_adopted')
    op.add_column('nodes', 'expiration_date', TIMESTAMP(timezone=True))
    op.drop_column('nodes', 'launched_at')
