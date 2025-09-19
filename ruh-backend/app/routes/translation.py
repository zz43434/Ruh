from flask import Blueprint, request, jsonify
import logging
from app.services.translation_service import TranslationService

translation_bp = Blueprint('translation', __name__)
translation_service = TranslationService()

@translation_bp.route('/translate', methods=['POST'])
def translate_verse():
    """
    Translate Arabic verse text to English using Groq API
    
    Expected JSON payload:
    {
        "arabic_text": "Arabic verse text to translate"
    }
    
    Returns:
    {
        "translation": "English translation of the verse",
        "status": "success"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'arabic_text' not in data:
            return jsonify({
                'error': 'arabic_text is required',
                'status': 'error'
            }), 400
        
        arabic_text = data['arabic_text'].strip()
        
        # Use the translation service to handle the translation
        result = translation_service.translate_arabic_to_english(arabic_text)
        
        # Check if there was an error
        if result.get('status') == 'error':
            error_code = 503 if 'service temporarily unavailable' in result.get('error', '') else 400
            return jsonify(result), error_code
            
        # Return successful translation
        return jsonify(result), 200
            
    except Exception as e:
        logging.error(f"Translation endpoint error: {e}")
        return jsonify({
            'error': 'Internal server error',
            'status': 'error'
        }), 500