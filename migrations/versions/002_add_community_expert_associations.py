"""add community and expert associations

Revision ID: 002
Revises: 001
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001_password_reset'
branch_labels = None
depends_on = None

def upgrade():
    # Create community_members association table
    op.create_table('community_members',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('community_id', sa.Integer(), nullable=False),
        sa.Column('joined_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['community_id'], ['communities.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('user_id', 'community_id')
    )
    
    # Create expert_followers association table
    op.create_table('expert_followers',
        sa.Column('follower_id', sa.Integer(), nullable=False),
        sa.Column('expert_id', sa.Integer(), nullable=False),
        sa.Column('followed_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['expert_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['follower_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('follower_id', 'expert_id')
    )
    
    # Add creator_id to communities table
    with op.batch_alter_table('communities', schema=None) as batch_op:
        batch_op.add_column(sa.Column('creator_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_communities_creator', 'users', ['creator_id'], ['id'])

def downgrade():
    with op.batch_alter_table('communities', schema=None) as batch_op:
        batch_op.drop_constraint('fk_communities_creator', type_='foreignkey')
        batch_op.drop_column('creator_id')
    
    op.drop_table('expert_followers')
    op.drop_table('community_members')
