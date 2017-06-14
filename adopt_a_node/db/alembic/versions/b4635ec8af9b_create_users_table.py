"""create users table

Revision ID: b4635ec8af9b
Revises:
Create Date: 2017-06-14 11:46:19.870414

"""
from alembic import op
from sqlalchemy import Column
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import INTEGER, TIMESTAMP, VARCHAR, BOOLEAN


# revision identifiers, used by Alembic.
revision = 'b4635ec8af9b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'users',
        Column('id', INTEGER, primary_key=True),
        Column('email', VARCHAR, nullable=False),
        Column('password', VARCHAR, nullable=False),
        Column('active', BOOLEAN),

        # Trackable
        Column('last_login_at', TIMESTAMP(timezone=True)),
        Column('current_login_at', TIMESTAMP(timezone=True)),
        Column('last_login_ip', VARCHAR),
        Column('current_login_ip', VARCHAR),
        Column('login_count', INTEGER),

        Column('created_at', TIMESTAMP(timezone=True), nullable=False, server_default=func.now()),
        Column('updated_at', TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    )

    op.create_index('unique_users_email', 'users', ['email'], unique=True)

def downgrade():
    op.drop_table('users')
