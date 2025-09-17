from flask import Blueprint, jsonify, request
from app.services.verse_service import VerseService

verses_bp = Blueprint('verses', __name__)
verse_service = VerseService()

@verses_bp.route('/verses', methods=['GET'])
def get_verses():
    verses = verse_service.get_all_verses()
    return jsonify(verses), 200

@verses_bp.route('/verses/<int:verse_id>', methods=['GET'])
def get_verse(verse_id):
    verse = verse_service.get_verse_by_id(verse_id)
    if verse:
        return jsonify(verse), 200
    return jsonify({'error': 'Verse not found'}), 404

@verses_bp.route('/verses', methods=['POST'])
def create_verse():
    data = request.json
    new_verse = verse_service.create_verse(data)
    return jsonify(new_verse), 201

@verses_bp.route('/verses/<int:verse_id>', methods=['PUT'])
def update_verse(verse_id):
    data = request.json
    updated_verse = verse_service.update_verse(verse_id, data)
    if updated_verse:
        return jsonify(updated_verse), 200
    return jsonify({'error': 'Verse not found'}), 404

@verses_bp.route('/verses/<int:verse_id>', methods=['DELETE'])
def delete_verse(verse_id):
    success = verse_service.delete_verse(verse_id)
    if success:
        return jsonify({'message': 'Verse deleted'}), 204
    return jsonify({'error': 'Verse not found'}), 404