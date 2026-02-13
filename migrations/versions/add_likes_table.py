"""Add likes table

Revision ID: add_likes_table
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_likes_table'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('likes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('post_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['post_id'], ['posts.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('post_id', 'user_id', name='unique_post_like')
    )
    op.create_index(op.f('ix_likes_post_id'), 'likes', ['post_id'], unique=False)
    op.create_index(op.f('ix_likes_user_id'), 'likes', ['user_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_likes_user_id'), table_name='likes')
    op.drop_index(op.f('ix_likes_post_id'), table_name='likes')
    op.drop_table('likes')
