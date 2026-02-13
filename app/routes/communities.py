from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request
from ..models.community import Community
from ..models.user import User
from ..extensions import db
from ..utils.validation import (
    validate_required_fields,
    validate_string_length,
    sanitize_string,
    validate_url
)

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
    @jwt_required(optional=True)
    def get(self):
        """Get all communities"""
        try:
            current_user_id = get_jwt_identity()
            page = request.args.get('page', 1, type=int)
            per_page = min(request.args.get('per_page', 20, type=int), 100)
            
            if page < 1:
                return {'error': 'Page must be >= 1'}, 400
            
            # Paginate communities
            paginated = Community.query.order_by(Community.created_at.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )
            
            return {
                'communities': [community.to_dict(current_user_id, include_counts=True) for community in paginated.items],
                'total': paginated.total,
                'pages': paginated.pages,
                'current_page': page
            }
        except Exception as e:
            return {'error': 'Failed to fetch communities'}, 500
    
    @community_ns.doc('create_community')
    @community_ns.expect(community_input)
    @community_ns.marshal_with(community_model, code=201)
    @jwt_required()
    def post(self):
        """Create a new community"""
        try:
            data = request.json
            
            # Validate required fields
            is_valid, error = validate_required_fields(data, ['name'])
            if not is_valid:
                return {'error': error}, 400
            
            # Sanitize and validate name
            name = sanitize_string(data['name'], 100)
            is_valid, error = validate_string_length(name, 3, 100, 'Name')
            if not is_valid:
                return {'error': error}, 400
            
            # Check duplicate
            if Community.query.filter_by(name=name).first():
                return {'error': 'Community with this name already exists'}, 400
            
            # Validate description
            description = sanitize_string(data.get('description'), 500)
            if description:
                is_valid, error = validate_string_length(description, 10, 500, 'Description')
                if not is_valid:
                    return {'error': error}, 400
            
            # Validate image URL
            image_url = sanitize_string(data.get('image_url'), 500)
            if image_url and not validate_url(image_url):
                return {'error': 'Invalid image URL format'}, 400
            
            # Validate category
            category = sanitize_string(data.get('category'), 50)
            
            community = Community(
                name=name,
                description=description,
                image_url=image_url,
                category=category
            )
            community.save()
            
            return community.to_dict(get_jwt_identity()), 201
        except Exception as e:
            db.session.rollback()
            return {'error': 'Failed to create community'}, 500

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
        try:
            from ..models import Comment, User
            
            messages = Comment.query.filter_by(community_id=id).order_by(Comment.created_at.asc()).limit(100).all()
            
            result = []
            for m in messages:
                author = User.query.get(m.author_id)
                result.append({
                    'id': m.id, 
                    'content': m.content, 
                    'author': {'name': author.full_name if author else 'Unknown'}, 
                    'created_at': m.created_at.isoformat()
                })
            
            return {'messages': result}
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {'error': str(e)}, 500
    
    @jwt_required()
    def post(self, id):
        """Send a message to community chat"""
        try:
            from ..models import Comment, User
            user_id = int(get_jwt_identity())
            data = request.get_json()
            
            # Validate content
            is_valid, error = validate_required_fields(data, ['content'])
            if not is_valid:
                return {'error': error}, 400
            
            content = sanitize_string(data.get('content'), 1000)
            is_valid, error = validate_string_length(content, 1, 1000, 'Message')
            if not is_valid:
                return {'error': error}, 400
            
            message = Comment(
                content=content,
                author_id=user_id,
                community_id=id
            )
            db.session.add(message)
            db.session.commit()
            
            author = User.query.get(user_id)
            return {
                'id': message.id, 
                'content': message.content, 
                'author': {'name': author.full_name if author else 'Unknown'}, 
                'created_at': message.created_at.isoformat()
            }, 201
        except Exception as e:
            db.session.rollback()
            import traceback
            traceback.print_exc()
            return {'error': str(e)}, 500
