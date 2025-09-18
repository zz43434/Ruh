import logging
from typing import Dict, Any, Optional
from app.core.groq_client import groq_client
from app.core import PROMPT_TEMPLATES
from app.models.verse_matcher import VerseMatcher

class ChatService:
    def __init__(self):
        self.verse_matcher = VerseMatcher(verses=[])
        self.groq_client = groq_client
        self.prompts = PROMPT_TEMPLATES
    
    def process_message(self, user_message: str, conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a user message through the complete pipeline
        """
        try:
            # Step 1: Analyze sentiment and themes
            sentiment_data = self._analyze_sentiment(user_message)
            
            # Step 2: Find relevant verses
            relevant_verses = self._find_relevant_verses(sentiment_data['themes'])
            
            # Step 3: Generate compassionate response
            response = self._generate_response(
                user_message, sentiment_data, relevant_verses
            )
            
            return {
                **response,
                "conversation_id": conversation_id or self._generate_conversation_id(),
                "timestamp": self._get_current_timestamp()
            }
            
        except Exception as e:
            logging.error(f"Error processing message: {e}")
            raise
    
    def _analyze_sentiment(self, user_message: str) -> Dict[str, Any]:
        """Analyze user message sentiment and themes"""
        prompt = self.prompts.get_sentiment_prompt(user_message)
        response = self.groq_client.generate_structured_response(prompt)
        return response
    
    def _find_relevant_verses(self, themes: list[str]) -> list[Dict[str, Any]]:
        """Find relevant Quranic verses based on themes"""
        return self.verse_matcher.find_relevant_verses(themes, top_k=3)
    
    def _generate_response(self, user_message: str, sentiment_data: Dict[str, Any], 
                               verses: list[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate compassionate response with Quranic guidance"""
        if not verses:
            # Fallback if no verses found
            return {
                "response": "I'm here to listen and provide support. Could you tell me more about how you're feeling?",
                "relevant_verses": [],
                "sentiment": sentiment_data['sentiment']
            }
        
        # Use the most relevant verse
        best_verse = verses[0]
        prompt = self.prompts.get_chat_prompt(
            user_message=user_message,
            sentiment=sentiment_data['sentiment'],
            themes=sentiment_data['themes'],
            verse_text=best_verse['text_translation'],
            surah_name=best_verse['surah_name'],
            verse_number=best_verse['verse_number']
        )
        
        response_text = self.groq_client.generate_response(prompt)
        
        return {
            "response": response_text,
            "relevant_verses": verses,
            "sentiment": sentiment_data['sentiment'],
            "themes": sentiment_data['themes']
        }
    
    def _generate_conversation_id(self) -> str:
        """Generate a unique conversation ID"""
        import uuid
        return str(uuid.uuid4())
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"