import datetime
from flask import current_app
from sqlalchemy import String, Column, text, ForeignKey, Boolean, Table, LargeBinary, DateTime, ARRAY
from sqlalchemy.orm import relationship
from .. import db, EnabledMixin
from .organization import Organization
from sqlalchemy.dialects.postgresql import UUID
from ...utils import verify_password_hash, generate_salt, hash_password_with_salt


class User(db.Model, EnabledMixin):
    __tablename__ = "user"

    id = Column(UUID(as_uuid=True), server_default=text("uuid_generate_v4()"), primary_key=True)
    firstname = Column(String(255), nullable=False)
    lastname = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    password_hash = Column(LargeBinary, nullable=False)
    password_salt = Column(LargeBinary, nullable=False)
    phone = Column(String(255), nullable=True)
    email_verified = Column(Boolean, default=False)
    phone_verified = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    reset_token = Column(String(1024))
    reset_token_sent_at = Column(String(64))
    verify_email_token = Column(String(36))
    verify_email_token_send_at = Column(String(64))
    prev_passwords = Column(ARRAY(LargeBinary))
    password_set_at = Column(DateTime(64))

    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organization.id", onupdate="cascade", ondelete="cascade"),
    )
    organization = relationship("Organization", back_populates="users")

    sites = relationship(
        "UserSite",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    ders = relationship(
        "UserDer",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    @property
    def password(self):
        raise AttributeError("Password is not a readable attribute")

    @password.setter
    def password(self, password):
        new_password = self.create_password_fields(password)
        self.password_salt = new_password["password_salt"]
        self.password_hash = new_password["password_hash"]
        self.password_set_at = new_password["password_set_at"]
        self.prev_passwords = new_password["prev_passwords"]

    def create_password_fields(self, password):
        fields = {"password_salt": generate_salt()}
        fields["password_hash"] = hash_password_with_salt(password, fields["password_salt"])
        fields["password_set_at"] = datetime.datetime.utcnow()
        if self.prev_passwords:
            fields["prev_passwords"] = [fields["password_salt"], fields["password_hash"]] + self.prev_passwords[0:4]
        else:
            fields["prev_passwords"] = [fields["password_salt"], fields["password_hash"]]
        return fields

    def is_password_used(self, password):
        if not self.prev_passwords:
            return False
        it = iter(self.prev_passwords)
        for password_salt, password_hash in zip(it, it):
            if verify_password_hash(password, password_hash, password_salt):
                return True
        return False

    def verify_password(self, password):
        if self.password_set_at:
            if self.password_set_at + datetime.timedelta(days=30 * 6) < datetime.datetime.now(datetime.timezone.utc):
                current_app.logger.error(f"Password is expired for user: {self.email}")
                return False
        return verify_password_hash(password, self.password_hash, self.password_salt)

    def to_dict(self, exclude_keys=("password_hash", "password_salt", "prev_passwords", "password_set_at")):
        return super(User, self).to_dict(exclude_keys)


Organization.users = relationship(
    "User",
    order_by=User.id,
    back_populates="organization",
    cascade="all, delete-orphan",
    passive_deletes=True,
)


class UserSite(db.Model):
    __tablename__ = "user_site"

    site_id = Column(
        UUID(as_uuid=True),
        ForeignKey("site.id", onupdate="cascade", ondelete="cascade"),
        primary_key=True,
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("user.id", onupdate="cascade", ondelete="cascade"),
        primary_key=True,
    )
    read_enabled = Column(Boolean, default=True, nullable=False)
    write_enabled = Column(Boolean, default=True, nullable=False)
    site = relationship("Site", back_populates="users")
    user = relationship("User", back_populates="sites")


class UserDer(db.Model):
    __tablename__ = "user_der"

    der_id = Column(
        UUID(as_uuid=True),
        ForeignKey("der.id", onupdate="cascade", ondelete="cascade"),
        primary_key=True,
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("user.id", onupdate="cascade", ondelete="cascade"),
        primary_key=True,
    )
    read_enabled = Column(Boolean, default=True, nullable=False)
    write_enabled = Column(Boolean, default=True, nullable=False)
    der = relationship("Der", back_populates="users")
    user = relationship("User", back_populates="ders")


class UsagePlan(db.Model, EnabledMixin):
    __tablename__ = "usage_plan"

    id = Column(UUID(as_uuid=True), server_default=text("uuid_generate_v4()"), primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("user.id", onupdate="cascade", ondelete="cascade"),
    )
    user = relationship("User", back_populates="usage_plan")

    apis = relationship(
        "Api",
        secondary="api_usage_plan",
        back_populates="usage_plans",
        passive_deletes=True,
    )
    api_key = relationship(
        "ApiKey",
        back_populates="usage_plan",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


User.usage_plan = relationship(
    "UsagePlan",
    order_by=UsagePlan.id,
    back_populates="user",
    uselist=False,
    cascade="all, delete-orphan",
    passive_deletes=True,
)


class ApiKey(db.Model, EnabledMixin):
    __tablename__ = "api_key"

    id = Column(UUID(as_uuid=True), server_default=text("uuid_generate_v4()"), primary_key=True)
    token = Column(String(4096), nullable=False, unique=False)
    usage_plan_id = Column(
        UUID(as_uuid=True),
        ForeignKey("usage_plan.id", onupdate="cascade", ondelete="cascade"),
    )
    usage_plan = relationship("UsagePlan", back_populates="api_key")


api_usage_plan_table = Table(
    "api_usage_plan",
    db.Model.metadata,
    Column(
        "api_id",
        ForeignKey("api.id", onupdate="cascade", ondelete="cascade"),
        primary_key=True,
    ),
    Column(
        "usage_plan_id",
        ForeignKey("usage_plan.id", onupdate="cascade", ondelete="cascade"),
        primary_key=True,
    ),
)
