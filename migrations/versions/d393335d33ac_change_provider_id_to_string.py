"""change provider_id to string

Revision ID: d393335d33ac
Revises: a237254c6f5a
Create Date: 2017-07-01 15:44:18.121507

"""
from alembic import op
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import INTEGER, VARCHAR


# revision identifiers, used by Alembic.
revision = 'd393335d33ac'
down_revision = 'a237254c6f5a'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('nodes', 'provider_id', type_=VARCHAR)

def downgrade():
    op.alter_column('nodes', 'provider_id', type_=INTEGER)
