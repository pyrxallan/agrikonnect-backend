from flask_restx import Namespace, Resource
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash, generate_password_hash
from ..models import User
from ..extensions import db

user_ns = Namespace('users', description='User operations')

@user_ns.route('/<int:user_id>')
class UserProfile(Resource):
    @jwt_required()
    def get(self, user_id):
        """Get user profile"""
        user = User.query.get_or_404(user_id)
        return user.to_dict()
    
    @jwt_required()
    def put(self, user_id):
        """Update user profile"""
        current_user_id = int(get_jwt_identity())
        if current_user_id != user_id:
            return {'message': 'Unauthorized'}, 403
        
        user = User.query.get_or_404(user_id)
        data = request.json
        
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        if 'email' in data:
            user.email = data['email']
        if 'phone' in data:
            user.phone = data['phone']
        if 'bio' in data:
            user.bio = data['bio']
        if 'location' in data:
            user.location = data['location']
        if 'farm_size' in data:
            user.farm_size = data['farm_size']
        if 'crops' in data:
            user.crops = data['crops']
        if 'profile_image' in data:
            user.profile_image = data['profile_image']
        if 'cover_image' in data:
            user.cover_image = data['cover_image']
        if 'is_public' in data:
            user.is_public = data['is_public']
        
        db.session.commit()
        return user.to_dict()

@user_ns.route('/<int:user_id>/password')
class UserPassword(Resource):
    @jwt_required()
    def put(self, user_id):
        """Change password"""
        current_user_id = int(get_jwt_identity())
        if current_user_id != user_id:
            return {'message': 'Unauthorized'}, 403
        
        user = User.query.get_or_404(user_id)
        data = request.json
        
        if not check_password_hash(user.password, data['current_password']):
            return {'message': 'Current password is incorrect'}, 400
        
        user.password = generate_password_hash(data['new_password'])
        db.session.commit()
        return {'message': 'Password changed successfully'}

@user_ns.route('/<int:user_id>/upload-photo')
class UserPhotoUpload(Resource):
    @jwt_required()
    def post(self, user_id):
        """Upload profile or cover photo"""
        current_user_id = int(get_jwt_identity())
        if current_user_id != user_id:
            return {'message': 'Unauthorized'}, 403
        
        if 'file' not in request.files:
            return {'message': 'No file provided'}, 400
        
        file = request.files['file']
        if file.filename == '':
            return {'message': 'No file selected'}, 400
        
        # Generate placeholder URL based on user
        user = User.query.get(user_id)
        name = f"{user.first_name}+{user.last_name}"
        placeholder_url = f'https://ui-avatars.com/api/?name={name}&size=400&background=2d5a2d&color=fff'
        
        # Update user profile
        photo_type = request.form.get('type', 'profile')
        if photo_type == 'profile':
            user.profile_image = placeholder_url
        else:
            user.cover_image = placeholder_url
        db.session.commit()
        
        return {'url': placeholder_url, 'message': 'Photo uploaded successfully'}
