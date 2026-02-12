from ..extensions import db
from .base import BaseModel

class Comment(BaseModel):
    __tablename__ = 'comments'

    content = db.Column(db.Text, nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=True, index=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    community_id = db.Column(db.Integer, db.ForeignKey('communities.id'), nullable=True, index=True)

    # Constraints
    __table_args__ = (
        db.CheckConstraint("length(content) >= 1", name='comment_content_not_empty'),
        db.Index('idx_comment_post_author', 'post_id', 'author_id'),
    )

    def to_dict(self):
        base_dict = super().to_dict()
        return {
            **base_dict,
            'content': self.content,
            'post_id': self.post_id,
            'author_id': self.author_id,
        }

    def __repr__(self):
        return f'<Comment {self.content[:30]}...>'
