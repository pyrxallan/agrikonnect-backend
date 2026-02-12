# like.py
from ..extensions import db
from .base import BaseModel

# This model represents a "Like" relationship between a User and a Post.

class Like(BaseModel):
    """
    Represents a 'Like' relationship between a User and a Post.
    This acts as an association table but uses a full model class 
    to allow for extra metadata (like timestamps from BaseModel).
    """
    __tablename__ = "likes"

    
    post_id = db.Column(
        db.Integer, 
        db.ForeignKey('posts.id'), 
        nullable=False,
        index=True  #slight optimization for queries that count likes for a specific post
    )
    
    user_id = db.Column(
        db.Integer, 
        db.ForeignKey('users.id'), 
        nullable=False,
        index=True  #slight optimization for queries that count likes by a specific user
    )

    # relationships that allow us to easily access the related Post and User objects from a Like instance
    post = db.relationship(
        'Post', 
        backref=db.backref('likes', lazy=True, cascade='all, delete-orphan')
    )
    
    user = db.relationship(
        'User', 
        backref=db.backref('likes', lazy=True, cascade='all, delete-orphan')
    )

    __table_args__ = (
        # Ensures a user cannot like the same post more than once
        db.UniqueConstraint("post_id", "user_id", name="uq_user_post_like"),
    )

    def __repr__(self):
        return f"<Like user_id={self.user_id} post_id={self.post_id}>"