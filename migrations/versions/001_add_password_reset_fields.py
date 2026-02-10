"""Add password reset fields to User model

Revision ID: 001_password_reset
Revises:
Create Date: 2024-01-29

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001_password_reset'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add password reset columns to users table
    op.add_column('users', sa.Column('password_reset_token', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('password_reset_expires', sa.DateTime(), nullable=True))


def downgrade():
    # Remove password reset columns from users table
    op.drop_column('users', 'password_reset_expires')
    op.drop_column('users', 'password_reset_token')
