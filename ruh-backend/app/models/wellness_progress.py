from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from app.models.database import Base

class WellnessProgress(Base):
    """
    Database model for tracking wellness progress.
    """
    __tablename__ = "wellness_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    mood = Column(String, nullable=False)
    energy_level = Column(Integer, nullable=False)
    stress_level = Column(Integer, nullable=False)
    notes = Column(Text, nullable=True)
    analysis = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
