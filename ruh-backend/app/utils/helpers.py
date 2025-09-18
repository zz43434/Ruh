from flask import request
import re

def validate_chat_request(req):
    """
    Validate chat request parameters
    """
    if not req.is_json:
        return "Request must be JSON"
    
    data = req.get_json()
    
    if 'message' not in data:
        return "Message field is required"
    
    if not isinstance(data['message'], str) or not data['message'].strip():
        return "Message must be a non-empty string"
    
    # Basic length validation
    if len(data['message'].strip()) > 1000:
        return "Message too long (max 1000 characters)"
    
    return None

def sanitize_input(text):
    """
    Basic input sanitization
    """
    if not text:
        return text
    
    # Remove potentially harmful characters
    text = re.sub(r'[<>{}]', '', text)
    # Trim whitespace
    text = text.strip()
    # Limit length
    return text[:1000]

def get_client_ip():
    """
    Get client IP address for rate limiting
    """
    if request.headers.getlist("X-Forwarded-For"):
        return request.headers.getlist("X-Forwarded-For")[0]
    else:
        return request.remote_addr