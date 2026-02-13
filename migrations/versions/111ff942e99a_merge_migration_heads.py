"""Merge migration heads

Revision ID: 111ff942e99a
Revises: a5ff909971d3, add_likes_table
Create Date: 2026-02-13 08:21:58.025430

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '111ff942e99a'
down_revision = ('a5ff909971d3', 'add_likes_table')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
