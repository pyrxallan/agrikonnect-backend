from flask import request
from flask_restx import Namespace, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
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