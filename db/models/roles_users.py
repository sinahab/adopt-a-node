

from sqlalchemy import Column, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import INTEGER, TIMESTAMP

from db.connection import db

roles_users = db.Table('roles_users',
        Column('user_id', INTEGER, ForeignKey('users.id')),
        Column('role_id', INTEGER, ForeignKey('roles.id')),
        Column('created_at', TIMESTAMP(timezone=True), nullable=False, server_default=func.now()),
        Column('updated_at', TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()))
