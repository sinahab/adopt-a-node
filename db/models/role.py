

from sqlalchemy import Column
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import INTEGER, TIMESTAMP, VARCHAR, TEXT
from flask_security import RoleMixin

from db.connection import db

class Role(db.Model, RoleMixin):
    __tablename__= 'roles'

    id = Column(INTEGER, primary_key=True)
    name = Column(VARCHAR, nullable=False)
    description = Column(TEXT)

    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return "Name(%r)" % (self.name)
