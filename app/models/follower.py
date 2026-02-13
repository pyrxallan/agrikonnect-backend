from ..extensions import db
from datetime import datetime

# Association table for user followers
followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('followed_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow)
)

# Association table for community members
community_members = db.Table('community_members',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('community_id', db.Integer, db.ForeignKey('communities.id'), primary_key=True),
    db.Column('joined_at', db.DateTime, default=datetime.utcnow)
)
