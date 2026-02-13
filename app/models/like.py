from ..extensions import db
from .base import BaseModel

class Like(BaseModel):
    __tablename__ = 'likes'

    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)

    __table_args__ = (
        db.UniqueConstraint('post_id', 'user_id', name='unique_post_like'),
    )

    def to_dict(self):
        return {
            **super().to_dict(),
            'post_id': self.post_id,
            'user_id': self.user_id
        }
