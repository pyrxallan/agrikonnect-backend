from flask_restx import Namespace, Resource, fields
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.community import Community
from ..models.user import User
from ..extensions import db

community_ns = Namespace('communities', description='Community operations')

community_model = community_ns.model('Community', {
    'id': fields.Integer(description='Community ID'),
    'name': fields.String(required=True, description='Community name'),
    'description': fields.String(description='Community description'),
    'members': fields.Integer(description='Number of members'),
    'creator_id': fields.Integer(description='Creator user ID')
})

@community_ns.route('')
class CommunityList(Resource):
    @jwt_required()
    def get(self):
        """Get all communities"""
        user_id = get_jwt_identity()
        communities = Community.query.all()
        
        result = []
        for c in communities:
            is_joined = db.session.execute(
                db.text('SELECT 1 FROM community_members WHERE user_id = :user_id AND community_id = :community_id'),
                {'user_id': user_id, 'community_id': c.id}
            ).first() is not None
            
            result.append({
                **c.to_dict(),
                'isJoined': is_joined
            })
        return result, 200

    @jwt_required()
    @community_ns.expect(community_model)
    def post(self):
        """Create a new community"""
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        # Only experts and admins can create communities
        if user.role not in ['expert', 'admin']:
            return {'message': 'Only experts and admins can create communities'}, 403
        
        data = request.get_json()
        
        if Community.query.filter_by(name=data['name']).first():
            return {'message': 'Community already exists'}, 400
        
        community = Community(
            name=data['name'], 
            description=data.get('description'),
            category=data.get('category'),
            creator_id=user_id
        )
        db.session.add(community)
        db.session.commit()
        
        # Auto-join creator
        community.members.append(user)
        db.session.commit()
        
        return community.to_dict(), 201

@community_ns.route('/<int:id>')
class CommunityDetail(Resource):
    @jwt_required()
    def get(self, id):
        """Get community details"""
        user_id = get_jwt_identity()
        community = Community.query.get_or_404(id)
        
        is_joined = db.session.execute(
            db.text('SELECT 1 FROM community_members WHERE user_id = :user_id AND community_id = :community_id'),
            {'user_id': user_id, 'community_id': id}
        ).first() is not None
        
        return {
            **community.to_dict(include_members=True),
            'isJoined': is_joined,
            'is_member': is_joined,
            'members_count': community.members.count()
        }, 200

    @jwt_required()
    @community_ns.expect(community_model)
    def put(self, id):
        """Update community"""
        user_id = get_jwt_identity()
        community = Community.query.get_or_404(id)
        
        if community.creator_id != user_id:
            return {'message': 'Unauthorized'}, 403
        
        data = request.get_json()
        community.name = data.get('name', community.name)
        community.description = data.get('description', community.description)
        community.category = data.get('category', community.category)
        db.session.commit()
        return community.to_dict(), 200

@community_ns.route('/<int:id>/join')
class CommunityJoin(Resource):
    @jwt_required()
    def post(self, id):
        """Join a community"""
        user_id = get_jwt_identity()
        community = Community.query.get_or_404(id)
        
        # Check if already a member using SQL
        existing = db.session.execute(
            db.text('SELECT 1 FROM community_members WHERE user_id = :user_id AND community_id = :community_id'),
            {'user_id': user_id, 'community_id': id}
        ).first()
        
        if existing:
            return {'message': 'Already a member'}, 400
        
        # Insert membership
        db.session.execute(
            db.text('INSERT INTO community_members (user_id, community_id) VALUES (:user_id, :community_id)'),
            {'user_id': user_id, 'community_id': id}
        )
        db.session.commit()
        return {'message': 'Joined successfully', 'community': community.to_dict()}, 200

@community_ns.route('/<int:id>/leave')
class CommunityLeave(Resource):
    @jwt_required()
    def post(self, id):
        """Leave a community"""
        user_id = get_jwt_identity()
        community = Community.query.get_or_404(id)
        
        # Check if member using SQL
        existing = db.session.execute(
            db.text('SELECT 1 FROM community_members WHERE user_id = :user_id AND community_id = :community_id'),
            {'user_id': user_id, 'community_id': id}
        ).first()
        
        if not existing:
            return {'message': 'Not a member'}, 400
        
        # Remove membership
        db.session.execute(
            db.text('DELETE FROM community_members WHERE user_id = :user_id AND community_id = :community_id'),
            {'user_id': user_id, 'community_id': id}
        )
        db.session.commit()
        return {'message': 'Left successfully', 'community': community.to_dict()}, 200

@community_ns.route('/<int:id>/delete')
class CommunityDelete(Resource):
    @jwt_required()
    def post(self, id):
        """Delete a community"""
        user_id = get_jwt_identity()
        community = Community.query.get_or_404(id)
        
        if community.creator_id != user_id:
            return {'message': 'Unauthorized'}, 403
        
        db.session.delete(community)
        db.session.commit()
        return {'message': 'Deleted successfully'}, 200
