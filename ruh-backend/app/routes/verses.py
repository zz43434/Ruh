from flask import Blueprint, request, jsonify
from app.services.verse_service import VerseService

verses_bp = Blueprint('verses', __name__)
verse_service = VerseService()

@verses_bp.route('/verses/search', methods=['GET', 'POST'])
def search_verses():
    """
    Search for Quranic verses by theme or keyword
    """
    try:
        if request.method == 'GET':
            theme = request.args.get('theme', '')
            max_results = int(request.args.get('max_results', 5))
            sort_by = request.args.get('sort_by', 'relevance')
        else:
            data = request.get_json()
            theme = data.get('theme', '')
            max_results = data.get('max_results', 5)
            sort_by = data.get('sort_by', 'relevance')
        
        if not theme:
            return jsonify({"error": "Theme parameter is required"}), 400
        
        results = verse_service.search_verses_by_theme(
            theme, max_results, sort_by
        )
        
        return jsonify({
            "verses": results,
            "search_query": theme,
            "total_results": len(results)
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@verses_bp.route('/verses/random', methods=['GET'])
def get_random_verse():
    """
    Get a random Quranic verse for daily inspiration
    """
    try:
        verse = verse_service.get_random_verse()
        return jsonify({"verse": verse}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500