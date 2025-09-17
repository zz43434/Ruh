from flask import Blueprint, request, jsonify
from app.services.chat_service import ChatService

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/chat', methods=['POST'])
def send_message():
    data = request.json
    response = ChatService.handle_message(data)
    return jsonify(response), 200

@chat_bp.route('/chat/history', methods=['GET'])
def get_chat_history():
    history = ChatService.get_chat_history()
    return jsonify(history), 200

@chat_bp.route('/chat/clear', methods=['DELETE'])
def clear_chat():
    ChatService.clear_chat_history()
    return jsonify({"message": "Chat history cleared"}), 204