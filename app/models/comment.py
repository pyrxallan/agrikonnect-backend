from ..extensions import db
from .base import BaseModel

class Comment(BaseModel):
    __tablename__ = 'comments'

    # Constraints so that content cannot be empty and author_id and post_id must be valid foreign keys
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False, index=True)

    __table_args__ = (
        db.CheckConstraint("length(content) >= 1", name='content_not_empty'),
    )

    # Relationships are defined in User and Post models with cascade delete, so no need to define them here
    def to_dict(self):
        base_dict = super().to_dict()
        return {
            **base_dict,
            'content': self.content,
            'author_id': self.author_id,
            'post_id': self.post_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }
    
    def __repr__(self):
        return f'<Comment id={self.id} author_id={self.author_id} post_id={self.post_id}>'
