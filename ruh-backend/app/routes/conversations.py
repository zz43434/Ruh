from flask import Blueprint, request, jsonify
from app.services.conversation_service import ConversationService

conversations_bp = Blueprint('conversations', __name__)
conversation_service = ConversationService()

@conversations_bp.route('/conversations', methods=['GET'])
def get_conversations():
    """
    Get conversation history (placeholder - would connect to DB)
    """
    try:
        user_id = request.args.get('user_id')
        limit = int(request.args.get('limit', 20))
        offset = int(request.args.get('offset', 0))
        
        # Placeholder - in production, this would query a database
        conversations = conversation_service.get_conversation_history(
            user_id, limit, offset
        )
        
        return jsonify({
            "conversations": conversations,
            "total_count": len(conversations)
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@conversations_bp.route('/conversations/<conversation_id>', methods=['GET'])
def get_conversation(conversation_id):
    """
    Get a specific conversation by ID
    """
    try:
        conversation = conversation_service.get_conversation_by_id(conversation_id)
        
        if not conversation:
            return jsonify({"error": "Conversation not found"}), 404
            
        return jsonify({"conversation": conversation}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500