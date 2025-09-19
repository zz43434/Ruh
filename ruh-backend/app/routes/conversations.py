from flask import Blueprint, request, jsonify
from app.services import conversation_service

conversations_bp = Blueprint('conversations', __name__)

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

@conversations_bp.route('/conversations/clear', methods=['DELETE'])
def clear_conversation_history():
    """
    Clear all conversation history for a user
    """
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({"error": "user_id parameter is required"}), 400
        
        result = conversation_service.clear_conversation_history(user_id)
        
        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 500
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@conversations_bp.route('/conversations/<conversation_id>/clear', methods=['DELETE'])
def clear_specific_conversation(conversation_id):
    """
    Clear a specific conversation and its messages
    """
    try:
        result = conversation_service.clear_specific_conversation(conversation_id)
        
        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 404 if "not found" in result["message"].lower() else 500
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500