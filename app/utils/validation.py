"""
Validation utilities for input sanitization and validation
"""
import re

def validate_email(email):
    """Validate email format"""
    if not email:
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength"""
    if not password:
        return False, "Password is required"
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    return True, None

def sanitize_string(text, max_length=None):
    """Sanitize string input"""
    if not text:
        return text
    text = str(text).strip()
    if max_length:
        text = text[:max_length]
    return text

def validate_required_fields(data, required_fields):
    """Validate that required fields are present"""
    missing = [field for field in required_fields if not data.get(field)]
    if missing:
        return False, f"Missing required fields: {', '.join(missing)}"
    return True, None

def validate_string_length(text, min_length=None, max_length=None, field_name="Field"):
    """Validate string length"""
    if not text:
        return False, f"{field_name} cannot be empty"
    
    length = len(text)
    if min_length and length < min_length:
        return False, f"{field_name} must be at least {min_length} characters"
    if max_length and length > max_length:
        return False, f"{field_name} must not exceed {max_length} characters"
    return True, None

def validate_integer_range(value, min_val=None, max_val=None, field_name="Value"):
    """Validate integer is within range"""
    try:
        value = int(value)
    except (ValueError, TypeError):
        return False, f"{field_name} must be a valid integer"
    
    if min_val is not None and value < min_val:
        return False, f"{field_name} must be at least {min_val}"
    if max_val is not None and value > max_val:
        return False, f"{field_name} must not exceed {max_val}"
    return True, None

def validate_url(url):
    """Validate URL format"""
    if not url:
        return True
    pattern = r'^https?://[^\s<>"{}|\\^`\[\]]+$'
    return re.match(pattern, url) is not None
