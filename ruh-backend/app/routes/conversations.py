from flask import Blueprint, request, jsonify
from app.services.conversation_service import ConversationService

conversations_bp = Blueprint('conversations', __name__)
conversation_service = ConversationService()

@conversations_bp.route('/conversations', methods=['GET'])
def get_conversations():
    conversations = conversation_service.get_all_conversations()
    return jsonify(conversations), 200

@conversations_bp.route('/conversations/<int:conversation_id>', methods=['GET'])
def get_conversation(conversation_id):
    conversation = conversation_service.get_conversation_by_id(conversation_id)
    if conversation:
        return jsonify(conversation), 200
    return jsonify({'error': 'Conversation not found'}), 404

@conversations_bp.route('/conversations', methods=['POST'])
def create_conversation():
    data = request.json
    new_conversation = conversation_service.create_conversation(data)
    return jsonify(new_conversation), 201

@conversations_bp.route('/conversations/<int:conversation_id>', methods=['PUT'])
def update_conversation(conversation_id):
    data = request.json
    updated_conversation = conversation_service.update_conversation(conversation_id, data)
    if updated_conversation:
        return jsonify(updated_conversation), 200
    return jsonify({'error': 'Conversation not found'}), 404

@conversations_bp.route('/conversations/<int:conversation_id>', methods=['DELETE'])
def delete_conversation(conversation_id):
    success = conversation_service.delete_conversation(conversation_id)
    if success:
        return jsonify({'message': 'Conversation deleted'}), 204
    return jsonify({'error': 'Conversation not found'}), 404