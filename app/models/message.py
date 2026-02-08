from ..extensions import db
from .base import BaseModel

class Message(BaseModel):
    __tablename__ = "messages"

    sender_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    receiver_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False, nullable=False)

    __table_args__ = (
        db.CheckConstraint("length(content) > 0", name="message_content_not_empty"),
        db.CheckConstraint("sender_id != receiver_id", name="no_self_messaging"),
        db.Index("idx_message_created_at", "created_at"),
    )

    def to_dict(self):
        data = super().to_dict()
        data.update({
            "sender_id": self.sender_id,
            "receiver_id": self.receiver_id,
            "content": self.content,
            "is_read": self.is_read,
        })
        return data

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.save()

    def __repr__(self):
        return f"<Message sender={self.sender_id} receiver={self.receiver_id}>"
