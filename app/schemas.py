"""
Input validation schemas for API endpoints
"""
from flask_restx import fields, Model
import re

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    return True, None

def validate_phone(phone):
    """Validate phone number format"""
    if not phone:
        return True
    pattern = r'^\+?1?\d{9,15}$'
    return re.match(pattern, phone.replace('-', '').replace(' ', '')) is not None

# Auth schemas
def get_auth_models(api):
    register_model = api.model('Register', {
        'email': fields.String(required=True, description='User email', example='farmer@example.com'),
        'password': fields.String(required=True, description='Password (min 8 chars, 1 uppercase, 1 lowercase, 1 number)', example='Password123'),
        'first_name': fields.String(required=True, min_length=1, max_length=50, description='First name', example='John'),
        'last_name': fields.String(required=True, min_length=1, max_length=50, description='Last name', example='Doe'),
        'role': fields.String(description='User role', enum=['farmer', 'expert'], default='farmer'),
        'phone': fields.String(description='Phone number', example='+1234567890'),
        'location': fields.String(max_length=100, description='Location', example='Nairobi, Kenya')
    })

    login_model = api.model('Login', {
        'email': fields.String(required=True, description='User email'),
        'password': fields.String(required=True, description='Password')
    })

    password_reset_request_model = api.model('PasswordResetRequest', {
        'email': fields.String(required=True, description='User email')
    })

    password_reset_model = api.model('PasswordReset', {
        'token': fields.String(required=True, description='Reset token'),
        'password': fields.String(required=True, description='New password')
    })

    return {
        'register': register_model,
        'login': login_model,
        'password_reset_request': password_reset_request_model,
        'password_reset': password_reset_model
    }

# Post schemas
def get_post_models(api):
    post_create_model = api.model('PostCreate', {
        'title': fields.String(required=True, min_length=1, max_length=255, description='Post title'),
        'content': fields.String(required=True, min_length=1, description='Post content'),
        'image_url': fields.String(max_length=500, description='Image URL'),
        'community_id': fields.Integer(description='Community ID if posting to community')
    })

    post_update_model = api.model('PostUpdate', {
        'title': fields.String(min_length=1, max_length=255, description='Post title'),
        'content': fields.String(min_length=1, description='Post content'),
        'image_url': fields.String(max_length=500, description='Image URL')
    })

    comment_create_model = api.model('CommentCreate', {
        'content': fields.String(required=True, min_length=1, max_length=1000, description='Comment content')
    })

    return {
        'post_create': post_create_model,
        'post_update': post_update_model,
        'comment_create': comment_create_model
    }

# Community schemas
def get_community_models(api):
    community_create_model = api.model('CommunityCreate', {
        'name': fields.String(required=True, min_length=3, max_length=100, description='Community name'),
        'description': fields.String(required=True, min_length=10, max_length=500, description='Community description'),
        'category': fields.String(max_length=50, description='Community category'),
        'image_url': fields.String(max_length=500, description='Community image URL'),
        'is_private': fields.Boolean(default=False, description='Is community private')
    })

    community_update_model = api.model('CommunityUpdate', {
        'name': fields.String(min_length=3, max_length=100, description='Community name'),
        'description': fields.String(min_length=10, max_length=500, description='Community description'),
        'category': fields.String(max_length=50, description='Community category'),
        'image_url': fields.String(max_length=500, description='Community image URL'),
        'is_private': fields.Boolean(description='Is community private')
    })

    return {
        'community_create': community_create_model,
        'community_update': community_update_model
    }

# User schemas
def get_user_models(api):
    user_update_model = api.model('UserUpdate', {
        'first_name': fields.String(min_length=1, max_length=50, description='First name'),
        'last_name': fields.String(min_length=1, max_length=50, description='Last name'),
        'bio': fields.String(max_length=500, description='User bio'),
        'location': fields.String(max_length=100, description='Location'),
        'phone': fields.String(description='Phone number'),
        'profile_image': fields.String(max_length=500, description='Profile image URL'),
        'cover_image': fields.String(max_length=500, description='Cover image URL'),
        'farm_size': fields.String(max_length=50, description='Farm size'),
        'crops': fields.String(max_length=255, description='Crops grown'),
        'title': fields.String(max_length=100, description='Professional title (for experts)'),
        'specialties': fields.List(fields.String, description='Expert specialties')
    })

    return {
        'user_update': user_update_model
    }

# Message schemas
def get_message_models(api):
    message_create_model = api.model('MessageCreate', {
        'receiver_id': fields.Integer(required=True, description='Receiver user ID'),
        'content': fields.String(required=True, min_length=1, max_length=1000, description='Message content')
    })

    return {
        'message_create': message_create_model
    }

# Expert schemas
def get_expert_models(api):
    rating_create_model = api.model('RatingCreate', {
        'rating': fields.Integer(required=True, min=1, max=5, description='Rating (1-5)'),
        'review': fields.String(max_length=500, description='Review text')
    })

    return {
        'rating_create': rating_create_model
    }
