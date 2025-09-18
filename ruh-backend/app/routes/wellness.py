from flask import Blueprint, request, jsonify
from app.services.wellness_service import WellnessService
from app.models.database import get_db

wellness_bp = Blueprint('wellness', __name__)
db = next(get_db())
wellness_service = WellnessService(db=db)

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
    Get wellness statistics and trends for a specific user.
    """
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({"error": "Missing required parameter: user_id"}), 400

        # Fetch tracked progress for the user
        progress_data = wellness_service.get_tracked_progress(user_id).get("progress", [])

        if not progress_data:
            return jsonify({
                "message": "No progress data found for the user.",
                "user_id": user_id,
                "stats": []
            }), 200

        # Pass the progress data to Groq for analysis
        groq_analysis = wellness_service.analyze_with_groq(progress_data)

        return jsonify({
            "message": "Wellness statistics retrieved successfully.",
            "user_id": user_id,
            "stats": groq_analysis
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500