from ..extensions import db
from .base import BaseModel

class Rating(BaseModel):
    __tablename__ = 'ratings'

    expert_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    review = db.Column(db.Text)

    __table_args__ = (
        db.CheckConstraint('rating >= 1 AND rating <= 5', name='valid_rating'),
        db.UniqueConstraint('expert_id', 'user_id', name='unique_user_expert_rating'),
    )

    def __repr__(self):
        return f'<Rating {self.rating} for expert {self.expert_id}>'
