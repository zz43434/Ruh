from flask import Blueprint, request, jsonify
from app.core.groq_client import groq_client
import logging

translation_bp = Blueprint('translation', __name__)

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
        
        if not arabic_text:
            return jsonify({
                'error': 'arabic_text cannot be empty',
                'status': 'error'
            }), 400
        
        # Create the translation prompt
        messages = [
            {
                "role": "system",
                "content": "You are a professional translator specializing in Arabic to English translation of Quranic verses. Provide only the English translation without any additional commentary, explanations, or formatting. Return only the translation text."
            },
            {
                "role": "user",
                "content": f"Translate this Arabic Quranic verse to English: {arabic_text}"
            }
        ]
        
        # Use the existing Groq client with streaming disabled for simpler response
        try:
            completion = groq_client._client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=messages,
                temperature=0.3,  # Lower temperature for more consistent translations
                max_tokens=500,
                top_p=1,
                stream=False,
                stop=None
            )
            
            translation = completion.choices[0].message.content.strip()
            
            return jsonify({
                'translation': translation,
                'status': 'success'
            }), 200
            
        except Exception as groq_error:
            logging.error(f"Groq API error: {groq_error}")
            return jsonify({
                'error': 'Translation service temporarily unavailable',
                'status': 'error'
            }), 503
            
    except Exception as e:
        logging.error(f"Translation endpoint error: {e}")
        return jsonify({
            'error': 'Internal server error',
            'status': 'error'
        }), 500