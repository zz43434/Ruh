# Shared service instances
from .conversation_service import ConversationService
from .chat_service import ChatService

# Create shared instances
conversation_service = ConversationService()
chat_service = ChatService()

# Make chat_service use the shared conversation_service
chat_service.conversation_service = conversation_service