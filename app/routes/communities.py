from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request
from ..models.community import Community
from ..models.user import User
from ..extensions import db

community_ns = Namespace('communities', description='Community operations')

# Response models
community_model = community_ns.model('Community', {
    'id': fields.Integer,
    'name': fields.String,
    'description': fields.String,
    'image_url': fields.String,
    'category': fields.String,
    'members_count': fields.Integer,
    'is_member': fields.Boolean,
    'created_at': fields.String,
    'updated_at': fields.String
})

community_input = community_ns.model('CommunityInput', {
    'name': fields.String(required=True),
    'description': fields.String,
    'image_url': fields.String,
    'category': fields.String
})

@community_ns.route('')
class CommunityList(Resource):
    @community_ns.doc('list_communities')
    @community_ns.marshal_list_with(community_model)
    @jwt_required(optional=True)
    def get(self):
        """Get all communities"""
        current_user_id = get_jwt_identity()
        communities = Community.query.all()
        
        return [community.to_dict(current_user_id, include_counts=True) for community in communities]
    
    @community_ns.doc('create_community')
    @community_ns.expect(community_input)
    @community_ns.marshal_with(community_model, code=201)
    @jwt_required()
    def post(self):
        """Create a new community"""
        data = request.json
        
        if Community.query.filter_by(name=data['name']).first():
            community_ns.abort(400, 'Community with this name already exists')
        
        community = Community(
            name=data['name'],
            description=data.get('description'),
            image_url=data.get('image_url'),
            category=data.get('category')
        )
        community.save()
        
        return community.to_dict(get_jwt_identity()), 201

@community_ns.route('/<int:id>')
class CommunityDetail(Resource):
    @community_ns.doc('get_community')
    @community_ns.marshal_with(community_model)
    @jwt_required(optional=True)
    def get(self, id):
        """Get community by ID"""
        current_user_id = get_jwt_identity()
        community = Community.query.get(id)
        if not community:
            community_ns.abort(404, 'Community not found')
        return community.to_dict(current_user_id)
    
    @community_ns.doc('update_community')
    @community_ns.expect(community_input)
    @community_ns.marshal_with(community_model)
    @jwt_required()
    def put(self, id):
        """Update a community"""
        community = Community.query.get(id)
        if not community:
            community_ns.abort(404, 'Community not found')
        
        data = request.json
        community.name = data.get('name', community.name)
        community.description = data.get('description', community.description)
        community.image_url = data.get('image_url', community.image_url)
        community.category = data.get('category', community.category)
        community.save()
        
        return community.to_dict(get_jwt_identity())
    
    @community_ns.doc('delete_community')
    @jwt_required()
    def delete(self, id):
        """Delete a community"""
        community = Community.query.get(id)
        if not community:
            community_ns.abort(404, 'Community not found')
        
        community.delete()
        return {'message': 'Community deleted successfully'}, 200

@community_ns.route('/<int:id>/join')
class CommunityJoin(Resource):
    @community_ns.doc('join_community')
    @jwt_required()
    def post(self, id):
        """Join a community"""
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        community = Community.query.get(id)
        
        if not community:
            community_ns.abort(404, 'Community not found')
        
        if current_user in community.members:
            community_ns.abort(400, 'Already a member of this community')
        
        community.members.append(current_user)
        db.session.commit()
        
        return {'message': 'Successfully joined community', 'is_member': True}, 200
    
    @community_ns.doc('leave_community')
    @jwt_required()
    def delete(self, id):
        """Leave a community"""
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        community = Community.query.get(id)
        
        if not community:
            community_ns.abort(404, 'Community not found')
        
        if current_user not in community.members:
            community_ns.abort(400, 'Not a member of this community')
        
        community.members.remove(current_user)
        db.session.commit()
        
        return {'message': 'Successfully left community', 'is_member': False}, 200

@community_ns.route('/<int:id>/members')
class CommunityMembers(Resource):
    @community_ns.doc('get_community_members')
    @jwt_required(optional=True)
    def get(self, id):
        """Get community members"""
        community = Community.query.get(id)
        if not community:
            community_ns.abort(404, 'Community not found')
        
        current_user_id = get_jwt_identity()
        members = list(community.members)
        return [member.to_dict(include_stats=True, current_user_id=current_user_id) for member in members]

@community_ns.route('/<int:id>/messages')
class CommunityMessages(Resource):
    @jwt_required()
    def get(self, id):
        """Get community chat messages"""
        from ..models import Comment
        messages = Comment.query.filter_by(community_id=id).order_by(Comment.created_at.asc()).limit(100).all()
        return {'messages': [{'id': m.id, 'content': m.content, 'author': {'name': m.author.full_name}, 'created_at': m.created_at.isoformat()} for m in messages]}
    
    @jwt_required()
    def post(self, id):
        """Send a message to community chat"""
        from ..models import Comment
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        message = Comment(
            content=data.get('content'),
            author_id=user_id,
            community_id=id
        )
        db.session.add(message)
        db.session.commit()
        
        return {'id': message.id, 'content': message.content, 'author': {'name': message.author.full_name}, 'created_at': message.created_at.isoformat()}, 201
