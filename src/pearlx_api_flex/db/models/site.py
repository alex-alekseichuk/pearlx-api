from sqlalchemy import Column, text, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.pearlx_api_flex.db import EnabledMixin, db


class Site(db.Model, EnabledMixin):

    __tablename__ = "site"

    id = Column(UUID(as_uuid=True), server_default=text("uuid_generate_v4()"), primary_key=True)
    site_id = Column(String(255), nullable=False, unique=True)
    site_name = Column(String(255), nullable=False)
    site_address = Column(String(255), nullable=False)
    system_id = Column(String(255), nullable=False)
    users = relationship(
        "UserSite",
        back_populates="site",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class Der(db.Model, EnabledMixin):

    __tablename__ = "der"

    id = Column(UUID(as_uuid=True), server_default=text("uuid_generate_v4()"), primary_key=True)
    der_id = Column(String(255), nullable=False, unique=True)
    der_type = Column(String(255), nullable=False)
    site_id = Column(
        UUID(as_uuid=True),
        ForeignKey("site.id", onupdate="cascade", ondelete="cascade"),
    )
    site = relationship("Site", back_populates="ders")
    users = relationship(
        "UserDer",
        back_populates="der",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


Site.ders = relationship(
    "Der",
    order_by=Der.id,
    back_populates="site",
    cascade="all, delete-orphan",
    passive_deletes=True,
)
