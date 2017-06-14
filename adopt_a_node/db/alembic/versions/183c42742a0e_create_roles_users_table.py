"""create roles_users table

Revision ID: 183c42742a0e
Revises: e4fd4c5d1906
Create Date: 2017-06-14 11:58:26.436737

"""
from alembic import op
from sqlalchemy import Column, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import INTEGER, TIMESTAMP

# revision identifiers, used by Alembic.
revision = '183c42742a0e'
down_revision = 'e4fd4c5d1906'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'roles_users',
        Column('id', INTEGER, primary_key=True),
        Column('user_id', INTEGER, ForeignKey('users.id')),
        Column('role_id', INTEGER, ForeignKey('roles.id')),

        Column('created_at', TIMESTAMP(timezone=True), nullable=False, server_default=func.now()),
        Column('updated_at', TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    )

    op.create_index('index_roles_users_on_user_id', 'roles_users', ['user_id'])
    op.create_index('index_roles_users_on_role_id', 'roles_users', ['role_id'])

def downgrade():
    op.drop_table('roles_users')
