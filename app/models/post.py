# post.py
from ..extensions import db
from .base import BaseModel

class Post(BaseModel):
    """
    Database model for user posts.
    Supports text content, images, and anonymous posting options.
    """
    __tablename__ = 'posts'

    
    # Title is optional but indexed for faster search sorting
    title = db.Column(db.String(200), nullable=True, index=True)
    
    # Main body of the post is required and can be of any length
    content = db.Column(db.Text, nullable=False)
    
    # Optional image URL associated with the post, with a length limit to prevent excessively long URLs
    image_url = db.Column(db.String(500), nullable=True)
    
    # If true, the author's identity is hidden
    is_anonymous = db.Column(db.Boolean, default=False, nullable=False)
    
    # Foreign Key that links to the User who created the post, indexed for faster queries filtering by author
    author_id = db.Column(
        db.Integer, 
        db.ForeignKey('users.id'), 
        nullable=False,
        index=True
    )

    __table_args__ = (
        # Ensure ppost content is not empty
        db.CheckConstraint("length(content) >= 1", name='check_content_min_length'),
    )

#relatinship to access comments related to a post, with cascading delete to ensure data integrity when a post is removed    
    comments = db.relationship(
        'Comment', 
        backref='post', 
        lazy=True,
        cascade='all, delete-orphan'
    )

    # property to calculate the number of comments on the fly, ensuring it reflects the current state of the database

    @property
    def comment_count(self):
        """Returns the current number of comments."""
        return len(self.comments)

    def to_dict(self):
        """
        Serializes the Post object to a dictionary.
        Merges base fields from BaseModel with post-specific data.
        """
        base_data = super().to_dict()
        
        # like count is calculated on the fly to ensure it reflects the current state of the database
        likes_count = 0
        if hasattr(self, 'likes'):
            likes_count = len(self.likes)

        return {
            **base_data,
            'title': self.title,
            'content': self.content,
            'image_url': self.image_url,
            'image': self.image_url,  # frontend compatibility
            'author_id': self.author_id,
            'is_anonymous': self.is_anonymous,
            'like_count': likes_count,
            'comment_count': self.comment_count,
        }

    def __repr__(self):
        safe_title = self.title if self.title else "Untitled"
        return f'<Post ID:{self.id} - "{safe_title[:20]}">'