# Import all models to ensure they are registered with SQLAlchemy
from .database import Base, engine, SessionLocal, get_db, init_db
from .conversation import Conversation, Message
from .wellness_progress import WellnessProgress

# Make sure all models are imported so they are registered with Base
__all__ = [
    'Base',
    'engine', 
    'SessionLocal',
    'get_db',
    'init_db',
    'Conversation',
    'Message',
    'WellnessProgress'
]