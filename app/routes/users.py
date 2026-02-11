from flask import request, Blueprint, jsonify
from flask_restx import Namespace, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from flask_cors import cross_origin
from app.models.user import User
from app.extensions import db

user_ns = Namespace('users', description='User operations')


@user_ns.route('/search')
class UserSearch(Resource):
    @jwt_required()
    def get(self):
        """Search users by name or email"""
        try:
            query = request.args.get('q', '').strip()
            user_id = get_jwt_identity()
            
            if not query:
                users = User.query.filter(User.id != user_id).limit(20).all()
            else:
                users = User.query.filter(
                    db.or_(
                        User.first_name.ilike(f'%{query}%'),
                        User.last_name.ilike(f'%{query}%'),
                        User.email.ilike(f'%{query}%')
                    )
                ).filter(User.id != user_id).limit(10).all()
            
            return [{
                'id': u.id,
                'first_name': u.first_name,
                'last_name': u.last_name,
                'email': u.email,
                'role': u.role
            } for u in users], 200
        except Exception as e:
            return {'error': str(e)}, 500


# Legacy Blueprint to support clients expecting /users/* (non-API path)
users_bp = Blueprint('users', __name__, url_prefix='/users')


@users_bp.route('/', methods=['GET', 'OPTIONS'], strict_slashes=False)
@cross_origin(origins=["http://localhost:5173", "http://localhost:3000", "http://localhost:5000"], supports_credentials=True)
def get_all_users():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        user_type = request.args.get('type', '').strip()
        
        query = User.query.filter(User.id != user_id)
        
        if user_type:
            query = query.filter(User.role == user_type)
        
        users = query.limit(20).all()
        
        return jsonify([{
            'id': u.id,
            'first_name': u.first_name,
            'last_name': u.last_name,
            'email': u.email,
            'role': u.role
        } for u in users]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 401


@users_bp.route('/search', methods=['GET', 'OPTIONS'], strict_slashes=False)
@cross_origin(origins=["http://localhost:5173", "http://localhost:3000", "http://localhost:5000"], supports_credentials=True)
def search_users():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        verify_jwt_in_request()
        query = request.args.get('q', '').strip()
        user_id = get_jwt_identity()
        
        if not query:
            users = User.query.filter(User.id != user_id).limit(20).all()
        else:
            users = User.query.filter(
                db.or_(
                    User.first_name.ilike(f'%{query}%'),
                    User.last_name.ilike(f'%{query}%'),
                    User.email.ilike(f'%{query}%')
                )
            ).filter(User.id != user_id).limit(10).all()
        
        return jsonify([{
            'id': u.id,
            'first_name': u.first_name,
            'last_name': u.last_name,
            'email': u.email,
            'role': u.role
        } for u in users]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 401

from flask_restx import Namespace, Resource
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from app.models.user import User
from app.extensions import db
import os

user_ns = Namespace('users', description='User operations')

@user_ns.route('/<int:id>')
class UserDetail(Resource):
    @jwt_required(optional=True)
    def get(self, id):
        user = User.query.get_or_404(id)
        return user.to_dict(include_stats=True, current_user_id=get_jwt_identity())
    
    @jwt_required()
    def put(self, id):
        if get_jwt_identity() != id:
            user_ns.abort(403, 'Forbidden')
        user = User.query.get_or_404(id)
        for key, value in request.json.items():
            if hasattr(user, key) and key != 'password':
                setattr(user, key, value)
        db.session.commit()
        return user.to_dict(include_stats=True, current_user_id=id)

@user_ns.route('/<int:id>/password')
class UserPassword(Resource):
    @jwt_required()
    def put(self, id):
        if get_jwt_identity() != id:
            user_ns.abort(403, 'Forbidden')
        user = User.query.get_or_404(id)
        if not check_password_hash(user.password, request.json.get('current_password', '')):
            user_ns.abort(400, 'Current password is incorrect')
        user.password = generate_password_hash(request.json['new_password'])
        db.session.commit()
        return {'message': 'Password changed successfully'}

@user_ns.route('/<int:id>/upload-photo')
class UserPhotoUpload(Resource):
    @jwt_required()
    def post(self, id):
        if get_jwt_identity() != id:
            user_ns.abort(403, 'Forbidden')
        user = User.query.get_or_404(id)
        file = request.files.get('file')
        if not file:
            user_ns.abort(400, 'No file provided')
        filename = secure_filename(f"{id}_{request.form.get('type', 'profile')}_{file.filename}")
        os.makedirs('uploads', exist_ok=True)
        file.save(os.path.join('uploads', filename))
        url = f"/uploads/{filename}"
        setattr(user, 'profile_image' if request.form.get('type') == 'profile' else 'cover_image', url)
        db.session.commit()
        return {'url': url}

@user_ns.route('/<int:user_id>/upload-photo')
class UserPhotoUpload(Resource):
    @jwt_required()
    def get(self):
        query = request.args.get('q', '').strip()
        user_id = get_jwt_identity()
        users = User.query.filter(User.id != user_id)
        if query:
            users = users.filter(db.or_(User.first_name.ilike(f'%{query}%'), User.last_name.ilike(f'%{query}%'), User.email.ilike(f'%{query}%')))
        return [{'id': u.id, 'first_name': u.first_name, 'last_name': u.last_name, 'email': u.email, 'role': u.role} for u in users.limit(20).all()]

