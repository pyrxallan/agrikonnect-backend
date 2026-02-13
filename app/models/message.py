from ..extensions import db
from .base import BaseModel

class Message(BaseModel):
    __tablename__ = 'messages'

    content = db.Column(db.Text, nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    is_read = db.Column(db.Boolean, default=False, nullable=False, server_default='false')

    # Constraints
    __table_args__ = (
        db.CheckConstraint("length(content) >= 1", name='message_content_not_empty'),
        db.CheckConstraint("sender_id != receiver_id", name='no_self_messaging'),
        db.Index('idx_message_sender_receiver', 'sender_id', 'receiver_id'),
        db.Index('idx_message_created_at', 'created_at'),
    )

    def to_dict(self):
        from .user import User
        base_dict = super().to_dict()
        sender = User.query.get(self.sender_id) if self.sender_id else None
        receiver = User.query.get(self.receiver_id) if self.receiver_id else None
        return {
            **base_dict,
            'content': self.content,
            'sender_id': self.sender_id,
            'receiver_id': self.receiver_id,
            'is_read': self.is_read,
            'sender': {
                'id': sender.id,
                'first_name': sender.first_name,
                'last_name': sender.last_name,
                'email': sender.email,
            } if sender else None,
            'receiver': {
                'id': receiver.id,
                'first_name': receiver.first_name,
                'last_name': receiver.last_name,
                'email': receiver.email,
            } if receiver else None,
        }

    def mark_as_read(self):
        """Mark the message as read"""
        self.is_read = True
        self.save()

    def __repr__(self):
        return f'<Message from {self.sender_id} to {self.receiver_id}>'
