from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request
from ..models.user import User
from ..extensions import db
from ..utils.validation import validate_integer_range

expert_ns = Namespace('experts', description='Expert operations')

# Response models
expert_model = expert_ns.model('Expert', {
    'id': fields.Integer,
    'name': fields.String,
    'avatar_url': fields.String,
    'title': fields.String,
    'location': fields.String,
    'specialties': fields.List(fields.String),
    'followers': fields.Integer,
    'posts': fields.Integer,
    'isVerified': fields.Boolean,
    'is_following': fields.Boolean,
    'bio': fields.String
})

@expert_ns.route('')
class ExpertList(Resource):
    @expert_ns.doc('list_experts')
    @jwt_required(optional=True)
    def get(self):
        """Get all experts"""
        try:
            current_user_id = get_jwt_identity()
            page = request.args.get('page', 1, type=int)
            per_page = min(request.args.get('per_page', 20, type=int), 100)
            
            if page < 1:
                return {'error': 'Page must be >= 1'}, 400
            
            # Paginate experts
            paginated = User.query.filter_by(role='expert', is_active=True).order_by(
                User.created_at.desc()
            ).paginate(page=page, per_page=per_page, error_out=False)
            
            return {
                'experts': [expert.to_expert_dict(current_user_id) for expert in paginated.items],
                'total': paginated.total,
                'pages': paginated.pages,
                'current_page': page
            }
        except Exception as e:
            return {'error': 'Failed to fetch experts'}, 500

@expert_ns.route('/specialties')
class ExpertSpecialties(Resource):
    @expert_ns.doc('list_specialties')
    def get(self):
        """Get all unique specialties from experts"""
        experts = User.query.filter_by(role='expert', is_active=True).all()
        specialties = set()
        for expert in experts:
            if expert.specialties:
                specialties.update(expert.specialties)
        return {'specialties': sorted(list(specialties))}

@expert_ns.route('/<int:id>')
class ExpertDetail(Resource):
    @expert_ns.doc('get_expert')
    @expert_ns.marshal_with(expert_model)
    @jwt_required(optional=True)
    def get(self, id):
        """Get expert by ID"""
        current_user_id = get_jwt_identity()
        expert = User.query.filter_by(id=id, role='expert').first()
        if not expert:
            expert_ns.abort(404, 'Expert not found')
        return expert.to_expert_dict(current_user_id)

@expert_ns.route('/<int:id>/follow')
class ExpertFollow(Resource):
    @expert_ns.doc('follow_expert')
    @jwt_required()
    def post(self, id):
        """Follow an expert"""
        try:
            # Validate ID
            is_valid, error = validate_integer_range(id, 1, None, 'Expert ID')
            if not is_valid:
                return {'error': error}, 400
            
            current_user_id = int(get_jwt_identity())
            
            if current_user_id == id:
                return {'error': 'Cannot follow yourself'}, 400
            
            current_user = User.query.get(current_user_id)
            expert = User.query.filter_by(id=id, role='expert').first()
            
            if not expert:
                return {'error': 'Expert not found'}, 404
            
            if expert in current_user.following.all():
                return {'error': 'Already following this expert'}, 400
            
            current_user.following.append(expert)
            db.session.commit()
            
            return {'message': 'Successfully followed expert', 'is_following': True}, 200
        except Exception as e:
            db.session.rollback()
            return {'error': 'Failed to follow expert'}, 500
    
    @expert_ns.doc('unfollow_expert')
    @jwt_required()
    def delete(self, id):
        """Unfollow an expert"""
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        expert = User.query.filter_by(id=id, role='expert').first()
        
        if not expert:
            expert_ns.abort(404, 'Expert not found')
        
        if expert not in current_user.following.all():
            expert_ns.abort(400, 'Not following this expert')
        
        current_user.following.remove(expert)
        db.session.commit()
        
        return {'message': 'Successfully unfollowed expert', 'is_following': False}, 200
