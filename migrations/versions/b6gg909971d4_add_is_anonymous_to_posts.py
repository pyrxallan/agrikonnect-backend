"""Add is_anonymous to posts

Revision ID: b6gg909971d4
Revises: a5ff909971d3
Create Date: 2026-02-12 09:40:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b6gg909971d4'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('posts', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_anonymous', sa.Boolean(), nullable=False, server_default='0'))


def downgrade():
    with op.batch_alter_table('posts', schema=None) as batch_op:
        batch_op.drop_column('is_anonymous')
