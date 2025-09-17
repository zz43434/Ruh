from flask import Blueprint, jsonify, request
from app.services.wellness_service import WellnessService

wellness_bp = Blueprint('wellness', __name__)

@wellness_bp.route('/wellness', methods=['GET'])
def get_wellness_resources():
    resources = WellnessService.get_resources()
    return jsonify(resources), 200

@wellness_bp.route('/wellness', methods=['POST'])
def create_wellness_resource():
    data = request.json
    new_resource = WellnessService.create_resource(data)
    return jsonify(new_resource), 201

@wellness_bp.route('/wellness/<int:resource_id>', methods=['GET'])
def get_wellness_resource(resource_id):
    resource = WellnessService.get_resource(resource_id)
    if resource:
        return jsonify(resource), 200
    return jsonify({'message': 'Resource not found'}), 404

@wellness_bp.route('/wellness/<int:resource_id>', methods=['PUT'])
def update_wellness_resource(resource_id):
    data = request.json
    updated_resource = WellnessService.update_resource(resource_id, data)
    if updated_resource:
        return jsonify(updated_resource), 200
    return jsonify({'message': 'Resource not found'}), 404

@wellness_bp.route('/wellness/<int:resource_id>', methods=['DELETE'])
def delete_wellness_resource(resource_id):
    success = WellnessService.delete_resource(resource_id)
    if success:
        return jsonify({'message': 'Resource deleted'}), 204
    return jsonify({'message': 'Resource not found'}), 404