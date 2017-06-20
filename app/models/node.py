

from sqlalchemy import Column, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import INTEGER, TIMESTAMP, VARCHAR, BOOLEAN
from sqlalchemy.orm import validates

from app import db

class Node(db.Model):
    __tablename__= 'nodes'

    id = Column(INTEGER, primary_key=True)
    user_id = Column(INTEGER, ForeignKey('users.id'))
    provider = Column(VARCHAR, nullable=False)
    ipv4_address = Column(VARCHAR)
    bu_ad = Column(INTEGER, nullable=False, server_default='16')
    bu_eb = Column(INTEGER, nullable=False, server_default='12')
    name = Column(VARCHAR)
    bu_version = Column(VARCHAR)
    status = Column(VARCHAR, nullable=False, server_default='initializing')
    expiration_date = Column(TIMESTAMP(timezone=True))

    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    user = db.relationship('User', back_populates='nodes')

    @validates('provider')
    def validate_email(self, key, provider):
        assert provider in ('aws', 'digital_ocean')
        return provider

    def __repr__(self):
        return "IPv4 Address(%r)" % (self.ipv4_address)
