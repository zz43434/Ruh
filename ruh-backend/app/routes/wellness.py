from flask import Blueprint, request, jsonify
from app.services.wellness_service import WellnessService
from app.models.database import get_db

wellness_bp = Blueprint('wellness', __name__)

@wellness_bp.route('/wellness', methods=['GET'])
def get_wellness_history():
    """
    Get wellness history and stats for a user
    Consolidated endpoint that handles both history and stats
    """
    try:
        db = next(get_db())
        wellness_service = WellnessService(db=db)
        
        user_id = request.args.get('user_id', 'default_user')
        limit = int(request.args.get('limit', 10))
        offset = int(request.args.get('offset', 0))
        
        history = wellness_service.get_wellness_history(user_id, limit=limit, offset=offset)
        
        response = {
            "wellness_history": history.get("wellness_history", []),
            "user_id": user_id,
            "total_entries": history.get("total_entries", 0)
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@wellness_bp.route('/wellness/checkin', methods=['POST'])
def wellness_checkin():
    """
    Submit a wellness check-in and get personalized guidance
    """
    try:
        db = next(get_db())
        wellness_service = WellnessService(db=db)
        
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

@wellness_bp.route('/wellness/ai-analysis', methods=['POST'])
def get_ai_wellness_analysis():
    """
    Get AI-powered wellness analysis with Islamic themes and verse recommendations.
    """
    try:
        db = next(get_db())
        wellness_service = WellnessService(db=db)
        
        data = request.get_json()
        
        if not data or 'user_id' not in data:
            return jsonify({"error": "Missing required field: user_id"}), 400
            
        user_id = data['user_id']
        
        # Get user's wellness history
        history = wellness_service.get_wellness_history(user_id)
        progress_data = history.get("wellness_history", [])
        
        # Check if there's any data - use a more lenient check
        if len(progress_data) == 0:
            return jsonify({
                "message": "Not enough wellness data for analysis.",
                "user_id": user_id,
                "analysis": None
            }), 200
            
        # Generate AI analysis
        analysis = wellness_service.analyze_with_groq(progress_data)
        
        return jsonify({
            "success": True,
            "user_id": user_id,
            "analysis": analysis
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@wellness_bp.route('/wellness/clear', methods=['DELETE'])
def clear_wellness_data():
    """
    Clear all wellness data for a user
    """
    try:
        db = next(get_db())
        wellness_service = WellnessService(db=db)
        
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({"error": "user_id parameter is required"}), 400
        
        result = wellness_service.clear_wellness_data(user_id)
        
        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 500
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@wellness_bp.route('/wellness/clear-all', methods=['DELETE'])
def clear_all_wellness_data():
    """
    Clear all wellness data for all users (admin function)
    """
    try:
        db = next(get_db())
        wellness_service = WellnessService(db=db)
        
        # Optional: Add admin authentication check here
        # admin_key = request.headers.get('X-Admin-Key')
        # if admin_key != 'your_admin_key':
        #     return jsonify({"error": "Unauthorized"}), 401
        
        result = wellness_service.clear_all_wellness_data()
        
        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 500
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
