from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from auth.models import Base


class PlatformOrg(Base):
    __tablename__ = 'platform_orgs'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    contact_name = Column(String(64), nullable=True)
    contact_phone = Column(String(20), nullable=True)
    status = Column(String(16), default='active')  # active, suspended
    created_at = Column(DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'contact_name': self.contact_name,
            'contact_phone': self.contact_phone,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class CommunityGroup(Base):
    __tablename__ = 'community_groups'

    id = Column(Integer, primary_key=True)
    platform_org_id = Column(Integer, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    address = Column(String(256), nullable=True)
    status = Column(String(16), default='active')  # active, suspended
    created_at = Column(DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'platform_org_id': self.platform_org_id,
            'name': self.name,
            'description': self.description,
            'address': self.address,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
