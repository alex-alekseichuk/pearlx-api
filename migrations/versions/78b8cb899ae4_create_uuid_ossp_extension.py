"""create uuid-ossp extension

Revision ID: 78b8cb899ae4
Revises: 
Create Date: 2022-03-24 19:51:06.774737

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "78b8cb899ae4"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    conn.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')


def downgrade():
    conn = op.get_bind()
    conn.execute('DROP EXTENSION IF EXISTS "uuid-ossp"')
