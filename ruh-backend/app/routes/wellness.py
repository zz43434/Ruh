from flask import Blueprint, request, jsonify
from app.services.wellness_service import WellnessService
from app.models.database import get_db

wellness_bp = Blueprint('wellness', __name__)

@wellness_bp.route('/wellness', methods=['GET'])
def get_wellness_history():
    """
    Get wellness history for a user
    """
    try:
        db = next(get_db())
        wellness_service = WellnessService(db=db)
        
        user_id = request.args.get('user_id', 'default_user')
        limit = int(request.args.get('limit', 10))
        
        history = wellness_service.get_tracked_progress(user_id)
        
        return jsonify({
            "wellness_history": history.get("progress", [])[:limit],
            "user_id": user_id,
            "total_entries": len(history.get("progress", []))
        }), 200
        
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

@wellness_bp.route('/wellness/stats', methods=['GET'])
def get_wellness_stats():
    """
    Get wellness statistics and trends for a specific user.
    """
    try:
        db = next(get_db())
        wellness_service = WellnessService(db=db)
        
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

@wellness_bp.route('/wellness/categories', methods=['GET'])
def get_wellness_categories():
    """
    Get all available wellness categories
    """
    try:
        wellness_service = WellnessService()
        
        categories = wellness_service.get_wellness_categories()
        
        return jsonify({
            "categories": categories,
            "total_categories": len(categories)
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@wellness_bp.route('/wellness/analyze', methods=['POST'])
def analyze_wellness_need():
    """
    Analyze user input to provide personalized Quranic guidance for wellness needs
    """
    try:
        wellness_service = WellnessService()
        
        data = request.get_json()
        
        if not data or 'user_input' not in data:
            return jsonify({"error": "Missing required field: user_input"}), 400
        
        user_input = data['user_input']
        max_verses = data.get('max_verses', 5)
        
        if not user_input.strip():
            return jsonify({"error": "User input cannot be empty"}), 400
        
        analysis_result = wellness_service.analyze_wellness_need(user_input, max_verses)
        
        return jsonify({
            "success": True,
            "analysis": analysis_result
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@wellness_bp.route('/wellness/category/<category_id>/verses', methods=['GET'])
def get_category_verses(category_id):
    """
    Get verses for a specific wellness category
    """
    try:
        wellness_service = WellnessService()
        
        max_verses = request.args.get('max_verses', 10, type=int)
        result = wellness_service.get_category_verses(category_id, max_verses)
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@wellness_bp.route('/wellness/guidance', methods=['POST'])
def get_wellness_guidance():
    """
    Get personalized wellness guidance based on user input
    """
    try:
        wellness_service = WellnessService()
        
        data = request.get_json()
        
        if not data or 'situation' not in data:
            return jsonify({"error": "Missing required field: situation"}), 400
        
        situation = data['situation']
        categories = data.get('categories', [])
        
        # Analyze the situation to get comprehensive guidance
        analysis = wellness_service.analyze_wellness_need(situation, max_verses=3)
        
        return jsonify({
            "success": True,
            "situation": situation,
            "guidance": analysis.get('guidance', ''),
            "detected_categories": analysis.get('detected_categories', []),
            "relevant_verses": analysis.get('verses', []),
            "recommendations": analysis.get('recommendations', [])
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500