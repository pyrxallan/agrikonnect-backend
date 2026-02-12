from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request
from ..models.user import User
from ..extensions import db

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
    @expert_ns.marshal_list_with(expert_model)
    @jwt_required(optional=True)
    def get(self):
        """Get all experts"""
        current_user_id = get_jwt_identity()
        experts = User.query.filter_by(role='expert', is_active=True).all()
        return [expert.to_expert_dict(current_user_id) for expert in experts]

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
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        expert = User.query.filter_by(id=id, role='expert').first()
        
        if not expert:
            expert_ns.abort(404, 'Expert not found')
        
        if current_user_id == id:
            expert_ns.abort(400, 'Cannot follow yourself')
        
        if expert in current_user.following.all():
            expert_ns.abort(400, 'Already following this expert')
        
        current_user.following.append(expert)
        db.session.commit()
        
        return {'message': 'Successfully followed expert', 'is_following': True}, 200
    
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
