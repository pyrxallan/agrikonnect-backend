from ..extensions import db
from .base import BaseModel

class Post(BaseModel):
    __tablename__ = 'posts'

    title = db.Column(db.String(200), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(500))
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)

    # Constraints
    __table_args__ = (
        db.CheckConstraint("length(title) >= 1", name='post_title_not_empty'),
        db.CheckConstraint("length(content) >= 1", name='post_content_not_empty'),
        db.CheckConstraint("length(title) <= 200", name='post_title_max_length'),
    )

    # Relationships
    comments = db.relationship('Comment', backref='post', lazy=True,
                              cascade='all, delete-orphan')

    def to_dict(self):
        base_dict = super().to_dict()
        return {
            **base_dict,
            'title': self.title,
            'content': self.content,
            'image_url': self.image_url,
            'author_id': self.author_id,
        }

    @property
    def comment_count(self):
        """Return the number of comments on this post"""
        return len(self.comments)

    def __repr__(self):
        return f'<Post {self.title[:30]}...>'
