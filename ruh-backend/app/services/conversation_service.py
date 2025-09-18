import uuid
from datetime import datetime
from typing import List, Dict, Optional
from app.services.verse_service import VerseService
from app.models.database import get_db
from app.models.conversation import Conversation, Message
from sqlalchemy.orm import Session

class ConversationService:
    def __init__(self):
        self.verse_service = VerseService()

    def start_conversation(self, user_id: str, initial_message: Optional[str] = None, db: Session = None) -> Dict:
        """Start a new conversation for a user."""
        conversation = Conversation(user_id=user_id)
        if initial_message:
            message = Message(conversation_id=conversation.id, sender="user", content=initial_message)
            conversation.messages.append(message)
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        return conversation

    def get_conversation_history(self, user_id: str, limit: int = 20, offset: int = 0) -> List[Dict]:
        """Get conversation history for a user."""
        db = get_db()
        conversations = db.query(Conversation).filter(Conversation.user_id == user_id).order_by(Conversation.updated_at.desc()).offset(offset).limit(limit).all()
        return [self._convert_to_dict(convo) for convo in conversations]

    def send_message(self, conversation_id: str, sender: str, content: str) -> Dict:
        """Send a message in a conversation."""
        db = get_db()
        conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if not conversation:
            raise ValueError("Conversation not found")
        
        message = Message(conversation_id=conversation_id, sender=sender, content=content)
        db.add(message)
        conversation.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(conversation)
        return self._convert_message_to_dict(message)

    def end_conversation(self, conversation_id: str) -> bool:
        """End a conversation."""
        db = get_db()
        conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if not conversation:
            return False
        
        conversation.status = 'ended'
        conversation.updated_at = datetime.utcnow()
        db.commit()
        return True

    def get_conversation_by_id(self, conversation_id: str) -> Optional[Dict]:
        """Get a specific conversation by ID."""
        db = get_db()
        conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        return self._convert_to_dict(conversation) if conversation else None

    def _generate_ai_response(self, user_message: str) -> str:
        """Generate AI response based on user message."""
        # Simple keyword-based responses with Quranic verses
        message_lower = user_message.lower()
        
        if any(word in message_lower for word in ['peace', 'calm', 'stress', 'anxiety']):
            verse = self.verse_service.get_verse("2:153")  # About patience and prayer
            if verse:
                return f"May Allah grant you peace. Remember: '{verse['arabic_text']}' - This verse reminds us to seek help through patience and prayer."
        
        elif any(word in message_lower for word in ['guidance', 'help', 'lost', 'confused']):
            verse = self.verse_service.get_verse("2:2")  # About guidance
            if verse:
                return f"Allah is the source of all guidance. '{verse['arabic_text']}' - This is the Book about which there is no doubt, a guidance for those conscious of Allah."
        
        elif any(word in message_lower for word in ['forgiveness', 'sin', 'mistake', 'repent']):
            verse = self.verse_service.get_verse("2:286")  # About Allah's mercy
            if verse:
                return f"Allah is Most Forgiving. '{verse['arabic_text']}' - Allah does not burden a soul beyond that it can bear."
        
        else:
            # Default response with random verse
            verse = self.verse_service.get_random_verse()
            return f"Thank you for sharing. Here's a verse for reflection: '{verse['arabic_text']}' - From Surah {verse['surah_name']} ({verse['verse_number']})"

    def analyze_conversation(self, conversation_data: Dict) -> Dict:
        """Analyze conversation for insights."""
        messages = conversation_data.get('messages', [])
        user_messages = [msg for msg in messages if msg['sender'] == 'user']
        
        return {
            'total_messages': len(messages),
            'user_messages': len(user_messages),
            'ai_messages': len(messages) - len(user_messages),
            'duration_minutes': self._calculate_duration(messages),
            'topics_discussed': self._extract_topics(user_messages)
        }
    
    def _calculate_duration(self, messages: List[Dict]) -> int:
        """Calculate conversation duration in minutes."""
        if len(messages) < 2:
            return 0
        
        start_time = datetime.fromisoformat(messages[0]['timestamp'])
        end_time = datetime.fromisoformat(messages[-1]['timestamp'])
        return int((end_time - start_time).total_seconds() / 60)
    
    def _extract_topics(self, user_messages: List[Dict]) -> List[str]:
        """Extract topics from user messages."""
        topics = set()
        for msg in user_messages:
            content = msg['content'].lower()
            if any(word in content for word in ['peace', 'calm', 'stress']):
                topics.add('peace_and_calm')
            if any(word in content for word in ['guidance', 'help', 'lost']):
                topics.add('guidance')
            if any(word in content for word in ['forgiveness', 'sin', 'repent']):
                topics.add('forgiveness')
        return list(topics)

    def _convert_to_dict(self, conversation: Conversation) -> Dict:
        """Convert Conversation SQLAlchemy object to dict."""
        if not conversation:
            return {}
        return {
            'id': conversation.id,
            'user_id': conversation.user_id,
            'created_at': conversation.created_at.isoformat(),
            'updated_at': conversation.updated_at.isoformat(),
            'status': conversation.status,
            'messages': [self._convert_message_to_dict(msg) for msg in conversation.messages]
        }

    def _convert_message_to_dict(self, message: Message) -> Dict:
        """Convert Message SQLAlchemy object to dict."""
        return {
            'id': message.id,
            'sender': message.sender,
            'content': message.content,
            'timestamp': message.timestamp.isoformat()
        }