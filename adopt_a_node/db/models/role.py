

from sqlalchemy import Column
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import INTEGER, TIMESTAMP, VARCHAR, TEXT

from adopt_a_node.db.models.base import Base

class Role(Base):
    __tablename__= 'roles'

    id = Column(INTEGER, primary_key=True)
    name = Column(VARCHAR, nullable=False)
    description = Column(TEXT)

    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    def __init__(self, name, description):
        self.name = name
        self.description = description

    def __repr__(self):
        return "Name(%r)" % (self.name)
