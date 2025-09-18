from flask import Blueprint, request, jsonify
from app.services.wellness_service import WellnessService

wellness_bp = Blueprint('wellness', __name__)
wellness_service = WellnessService()

@wellness_bp.route('/wellness/checkin', methods=['POST'])
def wellness_checkin():
    """
    Submit a wellness check-in and get personalized guidance
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['mood', 'energy_level', 'stress_level']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        result = wellness_service.process_wellness_checkin(
            mood=data['mood'],
            energy_level=data['energy_level'],
            stress_level=data['stress_level'],
            notes=data.get('notes', ''),
            user_id=data.get('user_id')
        )
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@wellness_bp.route('/wellness/stats', methods=['GET'])
def get_wellness_stats():
    """
    Get wellness statistics and trends (placeholder)
    """
    try:
        user_id = request.args.get('user_id')
        # This would connect to a database in production
        return jsonify({
            "message": "Wellness statistics endpoint",
            "user_id": user_id,
            "stats": {}  # Would contain actual stats
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500