"""add PearlX and Amalgam organizations

Revision ID: 0eeb823400b3
Revises: f3e659e271c0
Create Date: 2022-03-31 20:07:21.186059

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
from sqlalchemy import table, column, String

revision = "0eeb823400b3"
down_revision = "f3e659e271c0"
branch_labels = None
depends_on = None


def upgrade():
    organization_table = table(
        "organization",
        column("name", String),
        column("address", String),
        column("phone", String),
    )

    op.bulk_insert(
        organization_table,
        [
            {
                "name": "PearlX Infrastructure LLC",
                "address": "1612B Cambridge Circle, Charlottesville, VA-22903",
                "phone": None,
            },
            {
                "name": "Amalgam Inc.",
                "address": "840 1st Avenue; Suite 400, King of Prussia, PA 19406",
                "phone": "+1484354–8498",
            },
        ],
    )


def downgrade():
    op.execute(sa.text("DELETE FROM organization"))
