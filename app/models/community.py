from ..extensions import db
from .base import BaseModel

# Association table for community members
community_members = db.Table('community_members',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('community_id', db.Integer, db.ForeignKey('communities.id'), primary_key=True),
    db.Column('joined_at', db.DateTime, default=db.func.current_timestamp())
)

class Community(BaseModel):
    __tablename__ = 'communities'

    name = db.Column(db.String(100), nullable=False, unique=True, index=True)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relationships
    members = db.relationship('User', secondary=community_members, backref='communities', lazy='dynamic')
    creator = db.relationship('User', foreign_keys=[creator_id], backref='created_communities')

    # Constraints
    __table_args__ = (
        db.CheckConstraint("length(name) >= 1", name='community_name_not_empty'),
        db.CheckConstraint("length(name) <= 100", name='community_name_max_length'),
    )

    def to_dict(self, include_members=False):
        base_dict = super().to_dict()
        result = {
            **base_dict,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'members': self.members.count(),
            'creator_id': self.creator_id
        }
        if include_members:
            result['member_list'] = [m.to_dict() for m in self.members.all()]
        return result

    def __repr__(self):
        return f'<Community {self.name}>'
