from sqlalchemy import Column, text, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.pearlx_api_flex.db import EnabledMixin, db


class Api(db.Model, EnabledMixin):
    __tablename__ = "api"

    id = Column(UUID(as_uuid=True), server_default=text("uuid_generate_v4()"), primary_key=True)
    api_name = Column(String(255), nullable=False, unique=True)
    type = Column(String(255), nullable=False, unique=True)
    description = Column(String(1024), nullable=True, unique=True)

    usage_plans = relationship(
        "UsagePlan",
        secondary="api_usage_plan",
        back_populates="apis",
        passive_deletes=True,
    )
