"""add_admin_role

Revision ID: 5bd5513c9eea
Revises: d393335d33ac
Create Date: 2017-07-20 16:54:24.375100

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5bd5513c9eea'
down_revision = 'd393335d33ac'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    conn.execute("insert into roles (name, description) values ('admin', 'admin privileges')")

def downgrade():
    conn = op.get_bind()
    conn.execute("delete from roles where name='admin'")
