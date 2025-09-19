import logging
from app.core.groq_client import groq_client

class TranslationService:
    def __init__(self):
        self.groq_client = groq_client
    
    def translate_arabic_to_english(self, arabic_text):
        """
        Translate Arabic verse text to English using Groq API
        
        Args:
            arabic_text (str): Arabic text to translate
            
        Returns:
            dict: Dictionary containing translation and status
        """
        if not arabic_text or not arabic_text.strip():
            return {
                'error': 'arabic_text cannot be empty',
                'status': 'error'
            }
            
        # Define system prompt and user prompt
        system_prompt = "You are a professional translator specializing in Arabic to English translation of Quranic verses. Provide only the English translation without any additional commentary, explanations, or formatting. Return only the translation text."
        user_prompt = f"Translate this Arabic Quranic verse to English: {arabic_text}"
        
        try:
            # Use the groq_client.generate_response method
            translation = self.groq_client.generate_response(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.3,  # Lower temperature for more consistent translations
                max_tokens=500,
                model="llama-3.1-8b-instant"
            )
            
            return {
                'translation': translation.strip(),
                'status': 'success'
            }
            
        except Exception as groq_error:
            logging.error(f"Groq API error: {groq_error}")
            return {
                'error': 'Translation service temporarily unavailable',
                'status': 'error'
            }