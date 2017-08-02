

from sqlalchemy import Column
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import INTEGER, TIMESTAMP, VARCHAR, BOOLEAN
from flask_security import UserMixin, SQLAlchemyUserDatastore

from app import db
from .role import Role
from .roles_users import roles_users

class User(db.Model, UserMixin):
    __tablename__= 'users'

    id = Column(INTEGER, primary_key=True)
    email = Column(VARCHAR, nullable=False, unique=True)
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
    nodes = db.relationship('Node', back_populates='user')
    invoices = db.relationship('Invoice', back_populates='user')

    def __repr__(self):
        return "Email(%r)" % (self.email)

    def make_admin(self):
        """
        Makes the user an admin
        """
        user_datastore = SQLAlchemyUserDatastore(db, User, Role)
        user_datastore.add_role_to_user(self, 'admin')

    def unmake_admin(self):
        """
        Makes the user not an admin.
        """
        user_datastore = SQLAlchemyUserDatastore(db, User, Role)
        user_datastore.remove_role_from_user(self, 'admin')

from .node import Node
from .invoice import Invoice
