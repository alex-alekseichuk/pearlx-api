"""verify_email

Revision ID: 722a3bc08484
Revises: 67c24e129735
Create Date: 2022-08-28 13:25:50.729207

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "722a3bc08484"
down_revision = "67c24e129735"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("user", sa.Column("verify_email_token", sa.String(length=36), nullable=True))
    op.add_column("user", sa.Column("verify_email_token_send_at", sa.DateTime(), nullable=True))
    op.execute('UPDATE public."user" SET email_verified = TRUE WHERE is_admin = TRUE')


def downgrade():
    op.drop_column("user", "verify_email_token")
    op.drop_column("user", "verify_email_token_send_at")
