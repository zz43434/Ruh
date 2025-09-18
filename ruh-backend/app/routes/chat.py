from flask import Blueprint, request, jsonify
from app.services import chat_service
from app.utils.helpers import validate_chat_request

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/chat', methods=['POST'])
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

@chat_bp.route('/chat/verse-choice', methods=['POST'])
def handle_verse_choice():
    """
    Handle user's choice about viewing verses
    """
    # Validate request
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    data = request.get_json()
    
    # Debug logging to see what data we're receiving
    print(f"DEBUG: Received verse choice request with message_id: {data.get('message_id')}")
    print(f"DEBUG: Choice: {data.get('choice')}")
    
    # Validate required fields
    required_fields = ['choice', 'conversation_id', 'message_id', 'original_message']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"{field} is required"}), 400
    
    choice = data['choice']
    conversation_id = data['conversation_id']
    message_id = data['message_id']
    original_message = data['original_message']
    user_id = data.get('user_id', 'anonymous')
    
    try:
        # Process the verse choice through the service layer
        result = chat_service.handle_verse_choice(
            user_id=user_id,
            conversation_id=conversation_id,
            choice=choice,
            message_id=message_id,
            original_message=original_message
        )
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            "error": "Failed to process verse choice",
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