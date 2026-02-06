from ..extensions import db
from .base import BaseModel

#post model
class Post(BaseModel):
    __tablename__ = 'posts'

    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(255), nullable=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)

    __table_args__ = (
        db.CheckConstraint("length(title) >= 1", name='title_not_empty'),
        db.CheckConstraint("length(content) >= 1", name='content_not_empty'),
    )

    # Relationships with cascade delete
    comments = db.relationship('Comment', backref='post', lazy=True,
                               cascade='all, delete-orphan')
    likes = db.relationship('PostLike', backref='post', lazy=True,
                            cascade='all, delete-orphan')

    # Constraints to ensure title and content are not empty
    def to_dict(self):
        base_dict = super().to_dict()
        return {
            **base_dict,
            'title': self.title,
            'content': self.content,
            'author_id': self.author_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }
    
    def __repr__(self):
        return f'<Post id={self.id} title="{self.title}" author_id={self.author_id}>'
    
    
