from datetime import datetime
from ..extensions import db
from .base import BaseModel

# Association table for expert followers
expert_followers = db.Table('expert_followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    db.Column('expert_id', db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    db.Column('followed_at', db.DateTime, default=db.func.current_timestamp())
)

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
    profile_image = db.Column(db.String(255))
    specialties = db.Column(db.Text)  # JSON string of specialties
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
    ratings_received = db.relationship('Rating', foreign_keys='Rating.expert_id',
                                      backref='expert', lazy=True,
                                      cascade='all, delete-orphan')
    ratings_given = db.relationship('Rating', foreign_keys='Rating.user_id',
                                   backref='rater', lazy=True,
                                   cascade='all, delete-orphan')

    def is_following_expert(self, expert_id):
        result = db.session.execute(
            db.text('SELECT 1 FROM expert_followers WHERE follower_id = :follower_id AND expert_id = :expert_id'),
            {'follower_id': self.id, 'expert_id': expert_id}
        ).first()
        return result is not None
    
    def get_followers_count(self):
        result = db.session.execute(
            db.text('SELECT COUNT(*) as count FROM expert_followers WHERE expert_id = :expert_id'),
            {'expert_id': self.id}
        ).first()
        return result[0] if result else 0
    
    def get_average_rating(self):
        """Calculate average rating for expert"""
        result = db.session.execute(
            db.text('SELECT AVG(rating) as avg_rating FROM ratings WHERE expert_id = :expert_id'),
            {'expert_id': self.id}
        ).first()
        avg = result[0] if result and result[0] else 0
        return round(avg, 1) if avg else 0

    def to_dict(self, include_stats=False):
        base_dict = super().to_dict()
        result = {
            **base_dict,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'role': self.role,
            'bio': self.bio,
            'location': self.location,
            'profile_image': self.profile_image,
            'is_active': self.is_active,
        }
        if include_stats and self.role == 'expert':
            result['followers'] = self.followers.count()
            result['posts'] = len(self.posts)
        return result

    @property
    def full_name(self):
        """Return the user's full name"""
        return f"{self.first_name} {self.last_name}"

    def __repr__(self):
        return f'<User {self.email}>'
