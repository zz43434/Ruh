from flask import Blueprint, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from app.services import chat_service
from app.utils.helpers import validate_chat_request

chat_bp = Blueprint('chat', __name__)

# Create limiter instance
limiter = Limiter(
    app=None,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@chat_bp.route('/chat', methods=['POST'])
@limiter.limit("10 per minute")
def chat():
    """
    Main chat endpoint for processing user messages
    """
    # Validate request
    validation_error = validate_chat_request(request)
    if validation_error:
        return jsonify({"error": validation_error}), 400
    
    data = request.get_json()
    user_message = data['message']
    conversation_id = data.get('conversation_id')
    user_id = data.get('user_id')
    
    try:
        # Process the message through the service layer
        result = chat_service.process_message(
            user_message, 
            conversation_id,
            user_id or "anonymous"
        )
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            "error": "Failed to process message",
            "details": str(e)
        }), 500

@chat_bp.route('/chat/init', methods=['GET'])
def get_initial_message():
    """
    Get a welcoming initial message
    """
    try:
        welcome_message = {
            "response": "Assalamu alaikum! I'm Ruh, your Islamic wellness companion. I'm here to listen and provide spiritual comfort. How are you feeling today?",
            "conversation_id": chat_service._generate_conversation_id(),
            "timestamp": chat_service._get_current_timestamp()
        }
        return jsonify(welcome_message), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500