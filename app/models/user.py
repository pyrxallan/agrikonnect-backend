from datetime import datetime
from ..extensions import db
from .base import BaseModel

class User(BaseModel):
    __tablename__ = 'users'

    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='farmer',
                     server_default='farmer')
    bio = db.Column(db.Text)
    location = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    profile_image = db.Column(db.String(255))
    cover_image = db.Column(db.String(255))
    farm_size = db.Column(db.String(50))
    crops = db.Column(db.String(255))
    is_public = db.Column(db.Boolean, default=True, nullable=False, server_default='true')
    is_active = db.Column(db.Boolean, default=True, nullable=False,
                          server_default='true')

    # Password reset fields
    password_reset_token = db.Column(db.String(255), nullable=True)
    password_reset_expires = db.Column(db.DateTime, nullable=True)

    # Constraints
    __table_args__ = (
        db.CheckConstraint("role IN ('farmer', 'expert')", name='valid_role'),
        db.CheckConstraint("length(first_name) >= 1", name='first_name_not_empty'),
        db.CheckConstraint("length(last_name) >= 1", name='last_name_not_empty'),
        db.CheckConstraint("length(email) >= 3", name='email_min_length'),
    )

    # Relationships
    posts = db.relationship('Post', backref='author', lazy=True,
                           cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='author', lazy=True,
                              cascade='all, delete-orphan')
    messages_sent = db.relationship('Message', foreign_keys='Message.sender_id',
                                   backref='sender', lazy=True,
                                   cascade='all, delete-orphan')
    messages_received = db.relationship('Message', foreign_keys='Message.receiver_id',
                                       backref='receiver', lazy=True,
                                       cascade='all, delete-orphan')

    def to_dict(self):
        base_dict = super().to_dict()
        return {
            **base_dict,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'role': self.role,
            'bio': self.bio,
            'location': self.location,
            'phone': self.phone,
            'profile_image': self.profile_image,
            'cover_image': self.cover_image,
            'farm_size': self.farm_size,
            'crops': self.crops,
            'is_public': self.is_public,
            'is_active': self.is_active,
            'posts_count': len(self.posts) if hasattr(self, 'posts') else 0,
            'communities_count': 0,
        }

    @property
    def full_name(self):
        """Return the user's full name"""
        return f"{self.first_name} {self.last_name}"

    def __repr__(self):
        return f'<User {self.email}>'
