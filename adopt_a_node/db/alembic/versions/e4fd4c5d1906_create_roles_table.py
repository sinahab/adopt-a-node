"""create roles table

Revision ID: e4fd4c5d1906
Revises: b4635ec8af9b
Create Date: 2017-06-14 11:55:51.450620

"""
from alembic import op
from sqlalchemy import Column
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import INTEGER, TIMESTAMP, VARCHAR, TEXT

# revision identifiers, used by Alembic.
revision = 'e4fd4c5d1906'
down_revision = 'b4635ec8af9b'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'roles',
        Column('id', INTEGER, primary_key=True),
        Column('name', VARCHAR, nullable=False),
        Column('description', TEXT),

        Column('created_at', TIMESTAMP(timezone=True), nullable=False, server_default=func.now()),
        Column('updated_at', TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    )

    op.create_index('unique_roles_name', 'roles', ['name'], unique=True)

def downgrade():
    op.drop_table('roles')
