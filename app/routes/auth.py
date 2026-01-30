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

forgot_password_model = auth_ns.model('ForgotPassword', {
    'email': fields.String(required=True, description='User email')
})

reset_password_model = auth_ns.model('ResetPassword', {
    'token': fields.String(required=True, description='Password reset token'),
    'password': fields.String(required=True, description='New password')
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

        # Validate password strength
        password = data['password']
        if len(password) < 8:
            return {'message': 'Password must be at least 8 characters'}, 400

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
            'token': access_token,
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

        if not user.is_active:
            return {'message': 'Account is deactivated'}, 401

        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)

        return {
            'message': 'Login successful',
            'user': user.to_dict(),
            'token': access_token,
            'refresh_token': refresh_token
        }, 200


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
        user.password = generate_password_hash(new_password)
        user.password_reset_token = None
        user.password_reset_expires = None
        db.session.commit()

        return {'message': 'Password reset successful. You can now login with your new password'}, 200


@auth_ns.route('/refresh')
class TokenRefresh(Resource):
    @jwt_required(refresh=True)
    @auth_ns.response(200, 'Token refreshed')
    @auth_ns.response(401, 'Invalid refresh token')
    def post(self):
        """Refresh access token"""
        current_user_id = get_jwt_identity()

        # Verify user still exists and is active
        user = User.query.get(current_user_id)
        if not user or not user.is_active:
            return {'message': 'User not found or inactive'}, 401

        new_access_token = create_access_token(identity=current_user_id)

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
    @auth_ns.response(200, 'Current user data')
    @auth_ns.response(401, 'Unauthorized')
    def get(self):
        """Get current authenticated user"""
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            return {'message': 'User not found'}, 404

        return {
            'user': user.to_dict()
        }, 200
