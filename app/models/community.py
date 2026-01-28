from ..extensions import db
from .base import BaseModel

class Community(BaseModel):
    __tablename__ = 'communities'

    name = db.Column(db.String(100), nullable=False, unique=True, index=True)
    description = db.Column(db.Text)

    # Constraints
    __table_args__ = (
        db.CheckConstraint("length(name) >= 1", name='community_name_not_empty'),
        db.CheckConstraint("length(name) <= 100", name='community_name_max_length'),
    )

    def to_dict(self):
        base_dict = super().to_dict()
        return {
            **base_dict,
            'name': self.name,
            'description': self.description,
        }

    def __repr__(self):
        return f'<Community {self.name}>'
