<<<<<<< Updated upstream
from flask import request
from flask_restx import Namespace, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
=======
from flask import request, Blueprint, jsonify
from flask_restx import Namespace, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from flask_cors import cross_origin
>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
            return {'error': str(e)}, 500
=======
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
>>>>>>> Stashed changes
