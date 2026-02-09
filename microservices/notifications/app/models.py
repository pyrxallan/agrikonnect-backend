from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, index=True)
    type = db.Column(db.String(50), nullable=False)  # post_like, comment, follow, community_invite, expert_response
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    link = db.Column(db.String(500))
    is_read = db.Column(db.Boolean, default=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    actor_id = db.Column(db.Integer)  # User who triggered the notification
    actor_name = db.Column(db.String(100))
    actor_avatar = db.Column(db.String(500))
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'type': self.type,
            'title': self.title,
            'message': self.message,
            'link': self.link,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat(),
            'actor': {
                'id': self.actor_id,
                'name': self.actor_name,
                'avatar': self.actor_avatar
            } if self.actor_id else None
        }
