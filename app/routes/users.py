from flask import request, Blueprint, jsonify
from flask_restx import Namespace, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from app.models.user import User
from app.extensions import db
from app.utils.validation import (
    validate_password,
    validate_string_length,
    sanitize_string,
    validate_required_fields
)
import os

user_ns = Namespace('users', description='User operations')
users_bp = Blueprint('users', __name__)

@user_ns.route('/')
class UserList(Resource):
    @jwt_required()
    def get(self):
        query = request.args.get('q', '').strip()
        user_type = request.args.get('type', '').strip()
        user_id = int(get_jwt_identity())
        users = User.query.filter(User.id != user_id)
        if user_type and user_type != 'all':
            users = users.filter(User.role == user_type)
        if query:
            users = users.filter(db.or_(User.first_name.ilike(f'%{query}%'), User.last_name.ilike(f'%{query}%'), User.email.ilike(f'%{query}%')))
        return [{'id': u.id, 'first_name': u.first_name, 'last_name': u.last_name, 'email': u.email, 'role': u.role} for u in users.limit(20).all()]

@user_ns.route('/<int:id>')
class UserDetail(Resource):
    @jwt_required(optional=True)
    def get(self, id):
        user = User.query.get_or_404(id)
        return user.to_dict(include_stats=True, current_user_id=get_jwt_identity())
    
    @jwt_required()
    def put(self, id):
        """Update user profile"""
        try:
            if int(get_jwt_identity()) != id:
                return {'error': 'Forbidden'}, 403
            
            user = User.query.get(id)
            if not user:
                return {'error': 'User not found'}, 404
            
            data = request.json
            
            # Validate and update allowed fields
            if 'first_name' in data:
                first_name = sanitize_string(data['first_name'], 50)
                is_valid, error = validate_string_length(first_name, 1, 50, 'First name')
                if not is_valid:
                    return {'error': error}, 400
                user.first_name = first_name
            
            if 'last_name' in data:
                last_name = sanitize_string(data['last_name'], 50)
                is_valid, error = validate_string_length(last_name, 1, 50, 'Last name')
                if not is_valid:
                    return {'error': error}, 400
                user.last_name = last_name
            
            if 'bio' in data:
                bio = sanitize_string(data['bio'], 500)
                user.bio = bio

            if 'location' in data:
                location = sanitize_string(data['location'], 100)
                user.location = location

            if 'phone' in data:
                phone = sanitize_string(data['phone'], 20)
                user.phone = phone

            if 'farm_size' in data:
                user.farm_size = sanitize_string(data.get('farm_size'), 50)

            if 'crops' in data:
                user.crops = sanitize_string(data.get('crops'), 255)

            if 'is_public' in data:
                user.is_public = bool(data.get('is_public'))
            
            db.session.commit()
            return user.to_dict(include_stats=True, current_user_id=id)
        except Exception as e:
            db.session.rollback()
            return {'error': 'Failed to update profile'}, 500

@user_ns.route('/<int:id>/password')
class UserPassword(Resource):
    @jwt_required()
    def put(self, id):
        """Change user password"""
        try:
            if int(get_jwt_identity()) != id:
                return {'error': 'Forbidden'}, 403
            
            user = User.query.get(id)
            if not user:
                return {'error': 'User not found'}, 404
            
            data = request.json
            
            # Validate required fields
            is_valid, error = validate_required_fields(data, ['current_password', 'new_password'])
            if not is_valid:
                return {'error': error}, 400
            
            # Verify current password
            if not check_password_hash(user.password, data['current_password']):
                return {'error': 'Current password is incorrect'}, 400
            
            # Validate new password
            is_valid, error = validate_password(data['new_password'])
            if not is_valid:
                return {'error': error}, 400
            
            user.password = generate_password_hash(data['new_password'])
            db.session.commit()
            
            return {'message': 'Password changed successfully'}
        except Exception as e:
            db.session.rollback()
            return {'error': 'Failed to change password'}, 500

@user_ns.route('/<int:id>/upload-photo')
class UserPhotoUpload(Resource):
    @jwt_required()
    def post(self, id):
        """Upload user photo"""
        try:
            if int(get_jwt_identity()) != id:
                return {'error': 'Forbidden'}, 403
            
            user = User.query.get(id)
            if not user:
                return {'error': 'User not found'}, 404
            
            file = request.files.get('file')
            if not file:
                return {'error': 'No file provided'}, 400
            
            # Validate file type
            allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
            if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
                return {'error': 'Invalid file type. Allowed: png, jpg, jpeg, gif, webp'}, 400
            
            # Validate file size (5MB max)
            file.seek(0, 2)
            size = file.tell()
            file.seek(0)
            if size > 5 * 1024 * 1024:
                return {'error': 'File too large. Maximum size: 5MB'}, 400
            
            filename = secure_filename(f"{id}_{request.form.get('type', 'profile')}_{file.filename}")
            os.makedirs('uploads', exist_ok=True)
            file.save(os.path.join('uploads', filename))
            url = f"/uploads/{filename}"
            
            photo_type = request.form.get('type', 'profile')
            if photo_type == 'profile':
                user.profile_image = url
            else:
                user.cover_image = url
            
            db.session.commit()
            return {'url': url}
        except Exception as e:
            return {'error': 'Failed to upload photo'}, 500

# Blueprint routes for direct /users access
@users_bp.route('/users', methods=['GET'], strict_slashes=False)
@jwt_required(optional=True)
def get_users():
    current_user_id = get_jwt_identity()
    if not current_user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    user_id = int(current_user_id)
    query = request.args.get('q', '').strip()
    user_type = request.args.get('type', '').strip()
    
    users = User.query.filter(User.id != user_id)
    if user_type and user_type != 'all':
        users = users.filter(User.role == user_type)
    if query:
        users = users.filter(db.or_(User.first_name.ilike(f'%{query}%'), User.last_name.ilike(f'%{query}%'), User.email.ilike(f'%{query}%')))
    
    return jsonify([{'id': u.id, 'first_name': u.first_name, 'last_name': u.last_name, 'email': u.email, 'role': u.role} for u in users.limit(20).all()])

@users_bp.route('/users/search', methods=['GET'])
@jwt_required()
def search_users():
    user_id = int(get_jwt_identity())
    query = request.args.get('q', '').strip()
    user_type = request.args.get('type', '').strip()
    
    users = User.query.filter(User.id != user_id)
    if user_type and user_type != 'all':
        users = users.filter(User.role == user_type)
    if query:
        users = users.filter(db.or_(User.first_name.ilike(f'%{query}%'), User.last_name.ilike(f'%{query}%'), User.email.ilike(f'%{query}%')))
    
    return jsonify([{'id': u.id, 'first_name': u.first_name, 'last_name': u.last_name, 'email': u.email, 'role': u.role} for u in users.limit(20).all()])


@user_ns.route('/<int:id>/communities')
class UserCommunities(Resource):
    @jwt_required(optional=True)
    def get(self, id):
        """Get communities the user is a member of"""
        user = User.query.get_or_404(id)
        current_user_id = get_jwt_identity()
        # `communities` is a backref on the User model
        communities = list(getattr(user, 'communities', []))
        return [c.to_dict(current_user_id, include_counts=True) for c in communities]
