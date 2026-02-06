from ..extensions import db
from .base import BaseModel


class PostLike(BaseModel):
    __tablename__ = 'post_likes'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False, index=True)

    # Relationships
    user = db.relationship('User', backref=db.backref('post_likes', lazy=True, cascade='all, delete-orphan'))

    # Unique constraint to prevent duplicate likes
    __table_args__ = (
        db.UniqueConstraint('user_id', 'post_id', name='unique_user_post_like'),
    )
    def __repr__(self):
        return f'<PostLike user_id={self.user_id} post_id={self.post_id}>'  