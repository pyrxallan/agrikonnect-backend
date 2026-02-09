from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.user import User
from ..models.rating import Rating
from ..extensions import db

expert_ns = Namespace('experts', description='Expert operations')

expert_model = expert_ns.model('Expert', {
    'id': fields.Integer(description='Expert ID'),
    'name': fields.String(description='Expert name'),
    'title': fields.String(description='Expert title/role'),
    'location': fields.String(description='Expert location'),
    'bio': fields.String(description='Expert bio'),
    'followers': fields.Integer(description='Number of followers'),
    'posts': fields.Integer(description='Number of posts')
})

@expert_ns.route('')
class ExpertList(Resource):
    @jwt_required()
    def get(self):
        """Get all experts"""
        import json
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        experts = User.query.filter_by(role='expert').all()
        
        return [{
            'id': e.id,
            'name': e.full_name,
            'title': e.bio or 'Agricultural Expert',
            'location': e.location,
            'bio': e.bio,
            'specialties': json.loads(e.specialties) if e.specialties else [],
            'followers': e.get_followers_count(),
            'posts': len(e.posts),
            'rating': e.get_average_rating(),
            'is_following': current_user.is_following_expert(e.id),
            'avatar_url': e.profile_image
        } for e in experts], 200

@expert_ns.route('/<int:id>')
class ExpertDetail(Resource):
    @jwt_required()
    def get(self, id):
        """Get expert details"""
        import json
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        expert = User.query.filter_by(id=id, role='expert').first_or_404()
        
        return {
            'id': expert.id,
            'name': expert.full_name,
            'title': expert.bio or 'Agricultural Expert',
            'location': expert.location,
            'bio': expert.bio,
            'specialties': json.loads(expert.specialties) if expert.specialties else [],
            'followers': expert.get_followers_count(),
            'posts': len(expert.posts),
            'rating': expert.get_average_rating(),
            'is_following': current_user.is_following_expert(expert.id),
            'avatar_url': expert.profile_image,
            'email': expert.email
        }, 200

@expert_ns.route('/<int:id>/follow')
class ExpertFollow(Resource):
    @jwt_required()
    def post(self, id):
        """Follow an expert"""
        user_id = get_jwt_identity()
        expert = User.query.filter_by(id=id, role='expert').first_or_404()
        user = User.query.get(user_id)
        
        if user.is_following_expert(id):
            return {'message': 'Already following'}, 400
        
        db.session.execute(
            db.text('INSERT INTO expert_followers (follower_id, expert_id) VALUES (:follower_id, :expert_id)'),
            {'follower_id': user_id, 'expert_id': id}
        )
        db.session.commit()
        return {'message': 'Followed successfully'}, 200

@expert_ns.route('/<int:id>/unfollow')
class ExpertUnfollow(Resource):
    @jwt_required()
    def post(self, id):
        """Unfollow an expert"""
        user_id = get_jwt_identity()
        expert = User.query.filter_by(id=id, role='expert').first_or_404()
        user = User.query.get(user_id)
        
        if not user.is_following_expert(id):
            return {'message': 'Not following'}, 400
        
        db.session.execute(
            db.text('DELETE FROM expert_followers WHERE follower_id = :follower_id AND expert_id = :expert_id'),
            {'follower_id': user_id, 'expert_id': id}
        )
        db.session.commit()
        return {'message': 'Unfollowed successfully'}, 200

@expert_ns.route('/<int:id>/rate')
class ExpertRate(Resource):
    @jwt_required()
    def post(self, id):
        """Rate an expert"""
        from flask import request
        user_id = get_jwt_identity()
        expert = User.query.filter_by(id=id, role='expert').first_or_404()
        
        data = request.get_json()
        rating_value = data.get('rating')
        review = data.get('review', '')
        
        if not rating_value or rating_value < 1 or rating_value > 5:
            return {'message': 'Rating must be between 1 and 5'}, 400
        
        # Check if user already rated this expert
        existing_rating = Rating.query.filter_by(expert_id=id, user_id=user_id).first()
        
        if existing_rating:
            existing_rating.rating = rating_value
            existing_rating.review = review
        else:
            new_rating = Rating(expert_id=id, user_id=user_id, rating=rating_value, review=review)
            db.session.add(new_rating)
        
        db.session.commit()
        return {'message': 'Rating submitted successfully', 'average_rating': expert.get_average_rating()}, 200
