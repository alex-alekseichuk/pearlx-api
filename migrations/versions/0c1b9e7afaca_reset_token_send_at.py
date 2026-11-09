"""reset_token send_at

Revision ID: 0c1b9e7afaca
Revises: 722a3bc08484
Create Date: 2022-08-28 17:46:18.671016

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0c1b9e7afaca"
down_revision = "722a3bc08484"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("user", sa.Column("reset_token_sent_at", sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column("user", "reset_token_sent_at")
