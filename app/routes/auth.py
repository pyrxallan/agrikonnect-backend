from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import create_access_token, create_refresh_token
from werkzeug.security import generate_password_hash, check_password_hash

from ..models import User
from ..extensions import db

auth_ns = Namespace('auth', description='Authentication operations')

# Request/Response models
register_model = auth_ns.model('Register', {
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password'),
    'first_name': fields.String(required=True, description='First name'),
    'last_name': fields.String(required=True, description='Last name'),
    'role': fields.String(enum=['farmer', 'expert'], default='farmer', description='User role')
})

login_model = auth_ns.model('Login', {
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password')
})

@auth_ns.route('/register')
class Register(Resource):
    @auth_ns.expect(register_model)
    @auth_ns.response(201, 'User created successfully')
    @auth_ns.response(400, 'Validation error')
    def post(self):
        """Register a new user"""
        data = auth_ns.payload

        # Check if user already exists
        if User.query.filter_by(email=data['email']).first():
            return {'message': 'User already exists'}, 400

        # Create new user
        hashed_password = generate_password_hash(data['password'])
        user = User(
            email=data['email'],
            password=hashed_password,
            first_name=data['first_name'],
            last_name=data['last_name'],
            role=data.get('role', 'farmer')
        )

        db.session.add(user)
        db.session.commit()

        # Generate tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)

        return {
            'message': 'User created successfully',
            'user': user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token
        }, 201

@auth_ns.route('/login')
class Login(Resource):
    @auth_ns.expect(login_model)
    @auth_ns.response(200, 'Login successful')
    @auth_ns.response(401, 'Invalid credentials')
    def post(self):
        """Login user"""
        data = auth_ns.payload

        user = User.query.filter_by(email=data['email']).first()

        if not user or not check_password_hash(user.password, data['password']):
            return {'message': 'Invalid credentials'}, 401

        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)

        return {
            'message': 'Login successful',
            'user': user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token
        }, 200