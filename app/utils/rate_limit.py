"""
Rate limiting decorators for API endpoints
"""
from functools import wraps
from flask import current_app, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

def get_limiter():
    """Get limiter from current app"""
    return getattr(current_app, 'limiter', None)

def rate_limit(limit_string):
    """
    Rate limit decorator for Resource methods
    Usage: @rate_limit("5 per minute")
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            limiter = get_limiter()
            if limiter:
                # Apply rate limit
                limiter.limit(limit_string)(f)(*args, **kwargs)
            return f(*args, **kwargs)
        return decorated_function
    return decorator
