"""add ratings table

Revision ID: 003_add_ratings
Revises: 002_add_community_expert_associations
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003_add_ratings'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('ratings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('expert_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('review', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.CheckConstraint('rating >= 1 AND rating <= 5', name='valid_rating'),
        sa.ForeignKeyConstraint(['expert_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('expert_id', 'user_id', name='unique_user_expert_rating')
    )


def downgrade():
    op.drop_table('ratings')
