import uuid
from datetime import datetime
from typing import List, Dict, Optional
from app.services.verse_service import VerseService

class ConversationService:
    def __init__(self):
        # In-memory storage (use database in production)
        self.conversations = {}  # conversation_id -> conversation_data
        self.user_conversations = {}  # user_id -> [conversation_ids]
        self.verse_service = VerseService()

    def start_conversation(self, user_id: str, initial_message: Optional[str] = None) -> Dict:
        """Start a new conversation for a user."""
        conversation_id = str(uuid.uuid4())
        conversation = {
            'id': conversation_id,
            'user_id': user_id,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat(),
            'status': 'active',
            'messages': []
        }
        
        if initial_message:
            conversation['messages'].append({
                'id': str(uuid.uuid4()),
                'sender': 'user',
                'content': initial_message,
                'timestamp': datetime.utcnow().isoformat()
            })
        
        self.conversations[conversation_id] = conversation
        
        if user_id not in self.user_conversations:
            self.user_conversations[user_id] = []
        self.user_conversations[user_id].append(conversation_id)
        
        return conversation

    def get_conversation_history(self, user_id: str, limit: int = 20, offset: int = 0) -> List[Dict]:
        """Get conversation history for a user."""
        if user_id not in self.user_conversations:
            return []
        
        conversation_ids = self.user_conversations[user_id]
        conversations = [self.conversations[cid] for cid in conversation_ids if cid in self.conversations]
        
        # Sort by updated_at descending
        conversations.sort(key=lambda x: x['updated_at'], reverse=True)
        
        return conversations[offset:offset + limit]

    def send_message(self, conversation_id: str, sender: str, content: str) -> Dict:
        """Send a message in a conversation."""
        if conversation_id not in self.conversations:
            raise ValueError("Conversation not found")
        
        conversation = self.conversations[conversation_id]
        message = {
            'id': str(uuid.uuid4()),
            'sender': sender,
            'content': content,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        conversation['messages'].append(message)
        conversation['updated_at'] = datetime.utcnow().isoformat()
        
        return message

    def end_conversation(self, conversation_id: str) -> bool:
        """End a conversation."""
        if conversation_id not in self.conversations:
            return False
        
        self.conversations[conversation_id]['status'] = 'ended'
        self.conversations[conversation_id]['updated_at'] = datetime.utcnow().isoformat()
        return True

    def get_conversation_by_id(self, conversation_id: str) -> Optional[Dict]:
        """Get a specific conversation by ID."""
        return self.conversations.get(conversation_id)

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