"""add regular user

Revision ID: bc1b461b591b
Revises: e41f04296c95
Create Date: 2022-09-21 23:21:29.082111

"""
import os
import hashlib
import uuid
from alembic import op
import sqlalchemy as sa
from sqlalchemy import table, column, String, Boolean, LargeBinary
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = "bc1b461b591b"
down_revision = "e41f04296c95"
branch_labels = None
depends_on = None


user_table = table(
    "user",
    column("id", UUID),
    column("firstname", String),
    column("lastname", String),
    column("email", String),
    column("enabled", Boolean),
    column("is_admin", Boolean),
    column("password_hash", LargeBinary),
    column("password_salt", LargeBinary),
    column("organization_id", String),
    column("email_verified", Boolean),
    column("phone_verified", Boolean),
)

usage_plan_table = table(
    "usage_plan",
    column("name", String),
    column("enabled", Boolean),
    column("user_id", UUID),
)


def upgrade():
    salt = os.urandom(32)
    uuid_id = str(uuid.uuid4())

    conn = op.get_bind()
    res = conn.execute("SELECT id FROM organization WHERE name='PearlX Infrastructure LLC'")
    result = res.fetchone()
    organization_id = result["id"]

    op.bulk_insert(
        user_table,
        [
            {
                "id": uuid_id,
                "firstname": "flexapi",
                "lastname": "user",
                "email": "flexapi.user@pearlxinfra.com",
                "enabled": True,
                "is_admin": False,
                "password_hash": hashlib.pbkdf2_hmac(
                    "sha256", os.environ["ADMIN_PASSWORD"].encode("utf-8"), salt, 100000
                ),
                "password_salt": salt,
                "organization_id": organization_id,
                "email_verified": True,
                "phone_verified": True,
            },
        ],
    )

    op.bulk_insert(
        usage_plan_table,
        [
            {
                "name": "flexapi.user@pearlxinfra.com",
                "enabled": True,
                "user_id": uuid_id,
            },
        ],
    )

    op.execute(
        user_table.update()
        .where(user_table.c.email == "admin@some.com")
        .values(organization_id=organization_id)
    )


def downgrade():
    op.execute(usage_plan_table.delete().where(usage_plan_table.c.name == "flexapi.user@pearlxinfra.com"))
    op.execute(user_table.delete().where(user_table.c.email == "flexapi.user@pearlxinfra.com"))
