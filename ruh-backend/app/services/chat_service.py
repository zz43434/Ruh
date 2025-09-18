import logging
from typing import Dict, Any, Optional, List
from app.core.groq_client import groq_client
from app.core import PROMPT_TEMPLATES
from app.models.verse_matcher import VerseMatcher
from app.services.conversation_service import ConversationService
from app.services.verse_service import VerseService

class ChatService:
    def __init__(self):
        # Initialize verse service and get all verses for matching
        self.verse_service = VerseService()
        verse_texts = [verse['arabic_text'] for verse in self.verse_service.get_all_verses()]
        self.verse_matcher = VerseMatcher(verses=verse_texts)
        self.groq_client = groq_client
        self.prompts = PROMPT_TEMPLATES
        self.conversation_service = ConversationService()
    
    def process_message(self, user_message: str, conversation_id: Optional[str] = None, user_id: str = "anonymous") -> Dict[str, Any]:
        """
        Process a user message through the complete pipeline
        """
        try:
            # Get or create conversation with context
            conversation = self.conversation_service.get_or_create_conversation(user_id)
            conversation_context = self._get_conversation_context(conversation)
            
            # Add user message to conversation
            self.conversation_service.add_message(conversation['id'], user_message, 'user')
            
            # Step 1: Analyze sentiment and themes
            sentiment_data = self._analyze_sentiment(user_message)
            
            # Step 2: Find relevant verses
            relevant_verses = self._find_relevant_verses(sentiment_data['themes'])
            
            # Step 3: Generate AI response with context
            response = self._generate_response(
                user_message, sentiment_data, relevant_verses, conversation_context
            )
            
            # Add AI response to conversation
            self.conversation_service.add_message(conversation['id'], response["response"], 'assistant')
            
            return {
                **response,
                "conversation_id": conversation['id'],
                "timestamp": self._get_current_timestamp()
            }
            
        except Exception as e:
            logging.error(f"Error processing message: {e}")
            # Return a graceful error response instead of raising
            return {
                "response": "I apologize, but I'm experiencing some technical difficulties. Please try again in a moment.",
                "relevant_verses": [],
                "sentiment": "neutral",
                "themes": [],
                "conversation_id": conversation_id or "error",
                "timestamp": self._get_current_timestamp(),
                "error": True
            }
    
    def _analyze_sentiment(self, user_message: str) -> Dict[str, Any]:
        """Analyze user message sentiment, themes, and intent"""
        try:
            prompt = self.prompts.get_sentiment_prompt(user_message)
            response = self.groq_client.generate_structured_response(prompt)
            return response
        except Exception as e:
            logging.error(f"Error analyzing sentiment: {e}")
            # Return default sentiment data if analysis fails
            return {
                "sentiment": "neutral",
                "themes": ["general"],
                "intent": "general_chat",
                "confidence": 0.5
            }
    
    def _find_relevant_verses(self, themes: list[str]) -> list[Dict[str, Any]]:
        """Find relevant Quranic verses based on themes"""
        # Use the verse service to search for verses by theme
        relevant_verses = []
        for theme in themes:
            verses = self.verse_service.search_verses_by_theme(theme, max_results=2)
            relevant_verses.extend(verses)
        
        # Remove duplicates and limit to top 3
        seen_verses = set()
        unique_verses = []
        for verse in relevant_verses:
            verse_key = verse['verse_number']
            if verse_key not in seen_verses:
                seen_verses.add(verse_key)
                unique_verses.append(verse)
                if len(unique_verses) >= 3:
                    break
        
        return unique_verses
    
    def _generate_response(self, user_message: str, sentiment_data: Dict[str, Any], 
                           verses: list[Dict[str, Any]], conversation_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate response based on user intent and context"""
        intent = sentiment_data.get('intent', 'general_chat')
        
        # Handle different conversation intents
        if intent == 'general_chat':
            # For general chat, provide friendly Islamic conversation without forcing verses
            prompt = self.prompts.get_general_chat_prompt_with_context(
                user_message=user_message,
                sentiment=sentiment_data.get('sentiment', 'neutral'),
                conversation_context=conversation_context
            )
            
            response_text = self.groq_client.generate_response(prompt)
            
            return {
                "response": response_text,
                "relevant_verses": [],  # No verses for general chat
                "sentiment": sentiment_data.get('sentiment', 'neutral'),
                "themes": sentiment_data.get('themes', []),
                "intent": intent
            }
        
        elif intent in ['seeking_guidance', 'emotional_support']:
            # For guidance/support, offer verses with user choice
            if not verses:
                # Fallback if no verses found - use a random verse for inspiration
                fallback_verse = self.verse_service.get_random_verse()
                verses = [fallback_verse]
            
            # Instead of immediately providing verses, offer them as a choice
            prompt = self.prompts.get_general_chat_prompt_with_context(
                user_message=user_message,
                sentiment=sentiment_data.get('sentiment', 'neutral'),
                conversation_context=conversation_context
            )
            
            response_text = self.groq_client.generate_response(prompt)
            
            return {
                "response": response_text,
                "relevant_verses": verses,
                "sentiment": sentiment_data.get('sentiment', 'neutral'),
                "themes": sentiment_data.get('themes', []),
                "intent": intent,
                "verse_offer": {
                    "show_options": True,
                    "message": "I have some relevant Quranic verses that might provide comfort and guidance. Would you like me to share them with you?",
                    "options": [
                        {"id": "show_verses", "text": "Yes, please share the verses", "type": "primary"},
                        {"id": "continue_chat", "text": "No, let's continue our conversation", "type": "secondary"}
                    ]
                }
            }
        
        # Default fallback (shouldn't reach here, but just in case)
        return {
            "response": "I'm here to help. Could you tell me more about what you'd like to discuss?",
            "relevant_verses": [],
            "sentiment": sentiment_data.get('sentiment', 'neutral'),
            "themes": sentiment_data.get('themes', []),
            "intent": intent
        }

    def handle_verse_choice(self, user_id: str, conversation_id: str, choice: str, message_id: str, original_message: str) -> Dict[str, Any]:
        """Handle user's choice about viewing verses"""
        if choice == "primary":
            # Get conversation to retrieve the verse data from the last bot message
            conversation = self.conversation_service.get_conversation_by_id(conversation_id)
            conversation_context = self._get_conversation_context(conversation)
            
            # Find the most recent bot message that contains verse data
            verses = self._get_verses_from_last_response(conversation, original_message)
            
            if verses:
                # Generate response with verses and context
                best_verse = verses[0]
                prompt = self.prompts.get_chat_prompt(
                    user_message=original_message,
                    sentiment="neutral",
                    themes=[],
                    verse_text=best_verse['arabic_text'],
                    surah_name=best_verse['surah_name'],
                    verse_number=best_verse['verse_number'],
                    conversation_context=conversation_context
                )
                
                response_text = self.groq_client.generate_response(prompt)
                
                # Add the response to conversation
                self.conversation_service.add_message(conversation_id, response_text, 'assistant')
                
                return {
                    "response": response_text,
                    "relevant_verses": verses,
                    "sentiment": "neutral",
                    "themes": [],
                    "intent": "verse_sharing",
                    "conversation_id": conversation_id,
                    "timestamp": self._get_current_timestamp()
                }
            else:
                # Fallback if no verses found - regenerate them
                sentiment_data = self._analyze_sentiment(original_message)
                verses = self._find_relevant_verses(sentiment_data['themes'])
                
                if verses:
                    best_verse = verses[0]
                    prompt = self.prompts.get_chat_prompt(
                        user_message=original_message,
                        sentiment=sentiment_data.get('sentiment', 'neutral'),
                        themes=sentiment_data.get('themes', []),
                        verse_text=best_verse['arabic_text'],
                        surah_name=best_verse['surah_name'],
                        verse_number=best_verse['verse_number'],
                        conversation_context=conversation_context
                    )
                    
                    response_text = self.groq_client.generate_response(prompt)
                    self.conversation_service.add_message(conversation_id, response_text, 'assistant')
                    
                    return {
                        "response": response_text,
                        "relevant_verses": verses,
                        "sentiment": sentiment_data.get('sentiment', 'neutral'),
                        "themes": sentiment_data.get('themes', []),
                        "intent": "verse_sharing",
                        "conversation_id": conversation_id,
                        "timestamp": self._get_current_timestamp()
                    }
        
        elif choice == "continue_chat":
            # Continue normal conversation
            response_text = "Of course! I'm here to continue our conversation. What would you like to talk about?"
            
            # Add the response to conversation
            self.conversation_service.add_message(conversation_id, response_text, 'assistant')
            
            return {
                "response": response_text,
                "relevant_verses": [],
                "sentiment": "neutral",
                "themes": [],
                "intent": "general_chat",
                "conversation_id": conversation_id,
                "timestamp": self._get_current_timestamp()
            }
        
        # Default fallback
        return {
            "response": "I'm sorry, I didn't understand your choice. How can I help you?",
            "relevant_verses": [],
            "sentiment": "neutral",
            "themes": [],
            "intent": "general_chat",
            "conversation_id": conversation_id,
            "timestamp": self._get_current_timestamp()
        }

    def _get_verses_from_last_response(self, conversation: Dict[str, Any], original_message: str) -> List[Dict[str, Any]]:
        """Extract verses from the last bot response in conversation"""
        try:
            messages = conversation.get('messages', [])
            
            # Look for the most recent assistant message that contains relevant_verses
            for message in reversed(messages):
                if message.get('role') == 'assistant':
                    # Check if this message has metadata with verses
                    metadata = message.get('metadata', {})
                    if 'relevant_verses' in metadata:
                        return metadata['relevant_verses']
                    
                    # Also check if the message content contains verse data (fallback)
                    content = message.get('content', '')
                    if 'relevant_verses' in content:
                        # This is a fallback - in practice, verses should be in metadata
                        pass
            
            return []
        except Exception as e:
            print(f"Error extracting verses from conversation: {e}")
            return []

    def _get_conversation_context(self, conversation: Dict[str, Any]) -> Dict[str, Any]:
        if not conversation or 'messages' not in conversation:
            return {"is_new_conversation": True, "message_count": 0}
        
        messages = conversation['messages']
        message_count = len(messages)
        
        # Get recent messages (last 6 messages for context)
        recent_messages = messages[-6:] if len(messages) > 6 else messages
        
        # Check if this is early in the conversation
        is_new_conversation = message_count <= 2
        
        # Extract themes from recent user messages
        user_messages = [msg for msg in recent_messages if msg['sender'] == 'user']
        recent_themes = []
        for msg in user_messages:
            content = msg['content'].lower()
            if any(word in content for word in ['sad', 'down', 'depressed', 'upset']):
                recent_themes.append('emotional_support')
            elif any(word in content for word in ['blessed', 'good', 'happy', 'well']):
                recent_themes.append('positive')
        
        return {
            "is_new_conversation": is_new_conversation,
            "message_count": message_count,
            "recent_themes": recent_themes,
            "context_summary": f"Conversation with {message_count} messages, themes: {', '.join(recent_themes) if recent_themes else 'general'}"
        }
    
    def _generate_conversation_id(self) -> str:
        """Generate a unique conversation ID"""
        import uuid
        return str(uuid.uuid4())
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"