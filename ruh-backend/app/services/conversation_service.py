import uuid
from datetime import datetime
from typing import List, Dict, Optional
from app.services.verse_service import VerseService
from app.models.database import SessionLocal
from app.models.conversation import Conversation, Message
from sqlalchemy.orm import Session

class ConversationService:
    def __init__(self):
        self.verse_service = VerseService()

    def start_conversation(self, user_id: str, initial_message: Optional[str] = None) -> Dict:
        """Start a new conversation for a user."""
        db = SessionLocal()
        try:
            conversation = Conversation(user_id=user_id)
            db.add(conversation)
            db.flush()  # Get the ID without committing
            
            if initial_message:
                message = Message(
                    conversation_id=conversation.id, 
                    sender="user", 
                    content=initial_message
                )
                db.add(message)
            
            db.commit()
            db.refresh(conversation)
            return self._convert_to_dict(conversation)
        finally:
            db.close()

    def get_conversation_history(self, user_id: str, limit: int = 20, offset: int = 0) -> List[Dict]:
        """Get conversation history for a user."""
        db = SessionLocal()
        try:
            conversations = (db.query(Conversation)
                           .filter(Conversation.user_id == user_id)
                           .order_by(Conversation.updated_at.desc())
                           .offset(offset)
                           .limit(limit)
                           .all())
            return [self._convert_to_dict(convo) for convo in conversations]
        finally:
            db.close()

    def send_message(self, conversation_id: str, sender: str, content: str) -> Dict:
        """Send a message in a conversation."""
        db = SessionLocal()
        try:
            conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
            if not conversation:
                raise ValueError("Conversation not found")
            
            message = Message(conversation_id=conversation_id, sender=sender, content=content)
            db.add(message)
            conversation.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(message)
            return self._convert_message_to_dict(message)
        finally:
            db.close()

    def get_or_create_conversation(self, user_id: str) -> Dict:
        """Get the most recent active conversation for a user or create a new one."""
        db = SessionLocal()
        try:
            # Look for the most recent active conversation
            conversation = (db.query(Conversation)
                          .filter(Conversation.user_id == user_id)
                          .filter(Conversation.status == 'active')
                          .order_by(Conversation.updated_at.desc())
                          .first())
            
            if conversation:
                return self._convert_to_dict(conversation)
            else:
                # Create a new conversation
                return self.start_conversation(user_id)
        finally:
            db.close()

    def add_message(self, conversation_id: str, content: str, sender: str) -> Dict:
        """Add a message to a conversation."""
        return self.send_message(conversation_id, sender, content)


    def get_conversation_by_id(self, conversation_id: str) -> Optional[Dict]:
        """Get a specific conversation by ID."""
        db = SessionLocal()
        try:
            conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
            return self._convert_to_dict(conversation) if conversation else None
        finally:
            db.close()
    
    
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
    
    
    def clear_conversation_history(self, user_id: str) -> Dict:
        """Clear all conversation history for a user."""
        db = SessionLocal()
        try:
            # Get all conversations for the user
            conversations = db.query(Conversation).filter(Conversation.user_id == user_id).all()
            
            deleted_count = 0
            for conversation in conversations:
                # Delete all messages in the conversation
                db.query(Message).filter(Message.conversation_id == conversation.id).delete()
                # Delete the conversation
                db.delete(conversation)
                deleted_count += 1
            
            db.commit()
            return {
                "success": True,
                "message": f"Cleared {deleted_count} conversations for user {user_id}",
                "deleted_conversations": deleted_count
            }
        except Exception as e:
            db.rollback()
            return {
                "success": False,
                "message": f"Failed to clear conversation history: {str(e)}"
            }
        finally:
            db.close()

    def clear_specific_conversation(self, conversation_id: str) -> Dict:
        """Clear a specific conversation and its messages."""
        db = SessionLocal()
        try:
            conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
            if not conversation:
                return {
                    "success": False,
                    "message": "Conversation not found"
                }
            
            # Delete all messages in the conversation
            message_count = db.query(Message).filter(Message.conversation_id == conversation_id).count()
            db.query(Message).filter(Message.conversation_id == conversation_id).delete()
            
            # Delete the conversation
            db.delete(conversation)
            db.commit()
            
            return {
                "success": True,
                "message": f"Cleared conversation {conversation_id} with {message_count} messages",
                "deleted_messages": message_count
            }
        except Exception as e:
            db.rollback()
            return {
                "success": False,
                "message": f"Failed to clear conversation: {str(e)}"
            }
        finally:
            db.close()