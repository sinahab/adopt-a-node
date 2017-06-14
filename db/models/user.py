

from sqlalchemy import Column
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import INTEGER, TIMESTAMP, VARCHAR, BOOLEAN
from flask_security import UserMixin

from db.connection import db
from db.models.role import Role
from db.models.roles_users import roles_users

class User(db.Model, UserMixin):
    __tablename__= 'users'

    id = Column(INTEGER, primary_key=True)
    email = Column(VARCHAR, nullable=False)
    password = Column(VARCHAR, nullable=False)
    active = Column(BOOLEAN)

    # Trackable
    last_login_at = Column(TIMESTAMP(timezone=True))
    current_login_at = Column(TIMESTAMP(timezone=True))
    last_login_ip = Column(VARCHAR)
    current_login_ip = Column(VARCHAR)
    login_count = Column(INTEGER)

    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))

    def __repr__(self):
        return "Email(%r)" % (self.email)
