"""add admin user

Revision ID: b71832917b0c
Revises: 85d47f336da2
Create Date: 2022-04-15 21:31:09.431036

"""
import os
import hashlib
import uuid

from alembic import op

# revision identifiers, used by Alembic.
from sqlalchemy import table, column, String, Boolean, LargeBinary
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = "b71832917b0c"
down_revision = "85d47f336da2"
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

    op.bulk_insert(
        user_table,
        [
            {
                "id": uuid_id,
                "firstname": os.environ["ADMIN_FIRSTNAME"],
                "lastname": os.environ["ADMIN_LASTNAME"],
                "email": os.environ["ADMIN_EMAIL"],
                "enabled": True,
                "is_admin": True,
                "password_hash": hashlib.pbkdf2_hmac(
                    "sha256", os.environ["ADMIN_PASSWORD"].encode("utf-8"), salt, 100000
                ),
                "password_salt": salt,
            },
        ],
    )
    op.bulk_insert(
        usage_plan_table,
        [
            {
                "name": os.environ["ADMIN_EMAIL"],
                "enabled": True,
                "user_id": uuid_id,
            },
        ],
    )


def downgrade():
    op.execute(usage_plan_table.delete())
    op.execute(user_table.delete())
