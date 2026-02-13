import secrets
from datetime import datetime, timedelta
from flask import current_app
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)
from flask_mail import Message
from werkzeug.security import generate_password_hash, check_password_hash

from ..models import User
from ..extensions import db, mail
from .. import jwt_blocklist

auth_ns = Namespace('auth', description='Authentication operations')

# Request/Response models
register_model = auth_ns.model('Register', {
    'email': fields.String(required=True, description='User email address', example='user@example.com'),
    'password': fields.String(required=True, description='User password (min 8 characters)', example='password123'),
    'first_name': fields.String(required=True, description='User first name', example='John'),
    'last_name': fields.String(required=True, description='User last name', example='Doe'),
    'role': fields.String(enum=['farmer', 'expert'], default='farmer', description='User role', example='farmer')
})

login_model = auth_ns.model('Login', {
    'email': fields.String(required=True, description='User email address', example='user@example.com'),
    'password': fields.String(required=True, description='User password', example='password123')
})

user_response_model = auth_ns.model('UserResponse', {
    'id': fields.Integer(description='User ID'),
    'email': fields.String(description='User email'),
    'first_name': fields.String(description='First name'),
    'last_name': fields.String(description='Last name'),
    'role': fields.String(description='User role'),
    'bio': fields.String(description='User biography'),
    'location': fields.String(description='User location'),
    'profile_image': fields.String(description='Profile image URL'),
    'is_active': fields.Boolean(description='Account status'),
    'created_at': fields.DateTime(description='Account creation date'),
    'updated_at': fields.DateTime(description='Last update date')
})

auth_response_model = auth_ns.model('AuthResponse', {
    'message': fields.String(description='Response message'),
    'user': fields.Nested(user_response_model, description='User information'),
    'token': fields.String(description='JWT access token'),
    'refresh_token': fields.String(description='JWT refresh token')
})

forgot_password_model = auth_ns.model('ForgotPassword', {
    'email': fields.String(required=True, description='User email address', example='user@example.com')
})

reset_password_model = auth_ns.model('ResetPassword', {
    'token': fields.String(required=True, description='Password reset token from email'),
    'password': fields.String(required=True, description='New password (min 8 characters)', example='newpassword123')
})

token_response_model = auth_ns.model('TokenResponse', {
    'message': fields.String(description='Response message'),
    'token': fields.String(description='New JWT access token'),
    'refresh_token': fields.String(description='New JWT refresh token')
})


@auth_ns.route('/register')
class Register(Resource):
    @auth_ns.expect(register_model)
    @auth_ns.marshal_with(auth_response_model, code=201)
    @auth_ns.response(201, 'User created successfully', auth_response_model)
    @auth_ns.response(400, 'Validation error')
    @auth_ns.response(500, 'Internal server error')
    def post(self):
        """Register a new user"""
        try:
            data = auth_ns.payload or {}

            # Accept both snake_case and camelCase from frontend
            email = data.get('email')
            password = data.get('password')
            first_name = data.get('first_name') or data.get('firstName')
            last_name = data.get('last_name') or data.get('lastName')
            role = data.get('role') or data.get('userType') or data.get('user_type') or 'farmer'

            # Basic validation
            if not email or not password or not first_name or not last_name:
                return {'message': 'email, password, first_name and last_name are required'}, 400

            # Check if user already exists
            if User.query.filter_by(email=email).first():
                return {'message': 'User already exists'}, 400

            # Validate password strength
            if len(password) < 8:
                return {'message': 'Password must be at least 8 characters'}, 400

            # Create new user
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            
            # Handle specialties - convert string to array if needed
            specialties = data.get('specialties')
            if specialties and isinstance(specialties, str):
                specialties = [specialties]
            
            user = User(
                email=email,
                password=hashed_password,
                first_name=first_name,
                last_name=last_name,
                role=role,
                specialties=specialties if role == 'expert' else None
            )

            db.session.add(user)
            db.session.commit()

            # Generate tokens
            access_token = create_access_token(identity=str(user.id))
            refresh_token = create_refresh_token(identity=str(user.id))

            return {
                'message': 'User created successfully',
                'user': user.to_dict(),
                'token': access_token,
                'refresh_token': refresh_token
            }, 201
        except Exception as e:
            current_app.logger.exception(f"Error during register: {str(e)}")
            return {'message': 'Internal server error'}, 500


@auth_ns.route('/login')
class Login(Resource):
    @auth_ns.expect(login_model)
    @auth_ns.marshal_with(auth_response_model, code=200)
    @auth_ns.response(200, 'Login successful', auth_response_model)
    @auth_ns.response(400, 'Validation error')
    @auth_ns.response(401, 'Invalid credentials')
    @auth_ns.response(500, 'Internal server error')
    def post(self):
        """Login user"""
        try:
            data = auth_ns.payload or {}

            email = data.get('email')
            password = data.get('password')

            if not email or not password:
                return {'message': 'Email and password are required'}, 400

            user = User.query.filter_by(email=email).first()

            if not user or not check_password_hash(user.password, password):
                return {'message': 'Invalid credentials'}, 401

            if not user.is_active:
                return {'message': 'Account is deactivated'}, 401

            access_token = create_access_token(identity=str(user.id))
            refresh_token = create_refresh_token(identity=str(user.id))

            return {
                'message': 'Login successful',
                'user': user.to_dict(),
                'token': access_token,
                'refresh_token': refresh_token
            }, 200
        except Exception as e:
            current_app.logger.exception(f"Error during login: {str(e)}")
            return {'message': 'Internal server error'}, 500


@auth_ns.route('/forgot-password')
class ForgotPassword(Resource):
    @auth_ns.expect(forgot_password_model)
    @auth_ns.response(200, 'Password reset email sent')
    @auth_ns.response(404, 'User not found')
    def post(self):
        """Request password reset"""
        data = auth_ns.payload
        email = data.get('email')

        user = User.query.filter_by(email=email).first()

        # Always return success to prevent email enumeration
        if not user:
            return {'message': 'If an account exists with this email, a password reset link will be sent'}, 200

        # Generate reset token
        reset_token = secrets.token_urlsafe(32)
        expires = datetime.utcnow() + timedelta(
            seconds=current_app.config.get('PASSWORD_RESET_EXPIRES', 3600)
        )

        user.password_reset_token = reset_token
        user.password_reset_expires = expires
        db.session.commit()

        # Send reset email
        frontend_url = current_app.config.get('FRONTEND_URL', 'http://localhost:5173')
        reset_link = f"{frontend_url}/reset-password?token={reset_token}"

        try:
            msg = Message(
                subject='Agrikonnect - Password Reset Request',
                sender=current_app.config.get('MAIL_DEFAULT_SENDER'),
                recipients=[user.email]
            )
            msg.html = f"""
            <h2>Password Reset Request</h2>
            <p>Hello {user.first_name},</p>
            <p>You requested to reset your password for your Agrikonnect account.</p>
            <p>Click the link below to reset your password:</p>
            <p><a href="{reset_link}">Reset Password</a></p>
            <p>Or copy and paste this link into your browser:</p>
            <p>{reset_link}</p>
            <p>This link will expire in 1 hour.</p>
            <p>If you didn't request this, please ignore this email.</p>
            <br>
            <p>Best regards,<br>The Agrikonnect Team</p>
            """
            mail.send(msg)
        except Exception as e:
            # Log the error but don't expose it to the user
            current_app.logger.error(f"Failed to send password reset email: {str(e)}")

        return {'message': 'If an account exists with this email, a password reset link will be sent'}, 200


@auth_ns.route('/reset-password')
class ResetPassword(Resource):
    @auth_ns.expect(reset_password_model)
    @auth_ns.response(200, 'Password reset successful')
    @auth_ns.response(400, 'Invalid or expired token')
    def post(self):
        """Reset password with token"""
        data = auth_ns.payload
        token = data.get('token')
        new_password = data.get('password')

        # Validate password strength
        if len(new_password) < 8:
            return {'message': 'Password must be at least 8 characters'}, 400

        user = User.query.filter_by(password_reset_token=token).first()

        if not user:
            return {'message': 'Invalid or expired reset token'}, 400

        if user.password_reset_expires < datetime.utcnow():
            # Clear expired token
            user.password_reset_token = None
            user.password_reset_expires = None
            db.session.commit()
            return {'message': 'Reset token has expired. Please request a new one'}, 400

        # Update password
        user.password = generate_password_hash(new_password, method='pbkdf2:sha256')
        user.password_reset_token = None
        user.password_reset_expires = None
        db.session.commit()

        return {'message': 'Password reset successful. You can now login with your new password'}, 200


@auth_ns.route('/refresh')
class TokenRefresh(Resource):
    @jwt_required(refresh=True)
    @auth_ns.marshal_with(token_response_model, code=200)
    @auth_ns.response(200, 'Token refreshed', token_response_model)
    @auth_ns.response(401, 'Invalid refresh token')
    @auth_ns.response(500, 'Internal server error')
    def post(self):
        """Refresh access token"""
        current_user_id = get_jwt_identity()

        # Verify user still exists and is active
        user = User.query.get(current_user_id)
        if not user or not user.is_active:
            return {'message': 'User not found or inactive'}, 401

        new_access_token = create_access_token(identity=str(current_user_id))

        return {
            'message': 'Token refreshed',
            'token': new_access_token
        }, 200


@auth_ns.route('/logout')
class Logout(Resource):
    @jwt_required()
    @auth_ns.response(200, 'Logout successful')
    def post(self):
        """Logout user (revoke token)"""
        jti = get_jwt()['jti']
        jwt_blocklist.add(jti)
        return {'message': 'Successfully logged out'}, 200


@auth_ns.route('/me')
class CurrentUser(Resource):
    @jwt_required()
    @auth_ns.marshal_with(user_response_model, code=200)
    @auth_ns.response(200, 'Current user data', user_response_model)
    @auth_ns.response(401, 'Unauthorized')
    @auth_ns.response(404, 'User not found')
    def get(self):
        """Get current authenticated user"""
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            return {'message': 'User not found'}, 404

        return {
            'user': user.to_dict()
        }, 200


@auth_ns.route('/verify-token')
class VerifyToken(Resource):
    @jwt_required()
    @auth_ns.response(200, 'Token is valid')
    @auth_ns.response(401, 'Token is invalid or expired')
    def get(self):
        """Verify if the current JWT token is valid"""
        try:
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)

            if not user:
                return {'message': 'User not found'}, 401

            if not user.is_active:
                return {'message': 'Account is deactivated'}, 401

            return {
                'message': 'Token is valid',
                'user_id': current_user_id,
                'valid': True
            }, 200
        except Exception as e:
            current_app.logger.exception(f"Error verifying token: {str(e)}")
            return {'message': 'Token verification failed'}, 401
