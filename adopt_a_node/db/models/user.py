

from sqlalchemy import Column
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import INTEGER, TIMESTAMP, VARCHAR, BOOLEAN

from adopt_a_node.app import db

class User(db.Model):
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

    def __init__(self, email, password):
        self.email = email
        self.password = password

    def __repr__(self):
        return "Email(%r)" % (self.email)
