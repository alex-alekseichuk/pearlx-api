from sqlalchemy import String, Column, text
from src.pearlx_api_flex.db import db
from sqlalchemy.dialects.postgresql import UUID


class Organization(db.Model):
    __tablename__ = "organization"

    id = Column(UUID(as_uuid=True), server_default=text("uuid_generate_v4()"), primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    address = Column(String(255), nullable=False)
    org_type = Column(String(255), nullable=True)
    phone = Column(String(255), nullable=True)
