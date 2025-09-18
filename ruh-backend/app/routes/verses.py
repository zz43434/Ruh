from flask import Blueprint, request, jsonify
from app.services.verse_service import VerseService

verses_bp = Blueprint('verses', __name__)
verse_service = VerseService()

@verses_bp.route('/chapters', methods=['GET'])
def get_chapters():
    """
    Get a list of all Quranic chapters/surahs
    """
    try:
        chapters = verse_service.get_all_chapters()
        
        return jsonify({
            "chapters": chapters,
            "total_chapters": len(chapters)
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@verses_bp.route('/chapters/<int:surah_number>', methods=['GET'])
def get_chapter_details(surah_number):
    """
    Get detailed information about a specific chapter including its verses with translations
    """
    try:
        chapter = verse_service.get_chapter_with_verses(surah_number)
        
        if not chapter:
            return jsonify({"error": "Chapter not found"}), 404
            
        return jsonify({
            "chapter": chapter
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@verses_bp.route('/verses', methods=['GET'])
def get_verses():
    """
    Get a list of Quranic verses
    """
    try:
        limit = int(request.args.get('limit', 10))
        offset = int(request.args.get('offset', 0))
        
        verses = verse_service.get_verses(limit=limit, offset=offset)
        
        return jsonify({
            "verses": verses,
            "limit": limit,
            "offset": offset,
            "total_results": len(verses)
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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