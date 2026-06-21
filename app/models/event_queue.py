from sqlalchemy import Column, Integer, String, DateTime, JSON
from datetime import datetime
from app.db.base import Base

class EventQueue(Base):
    __tablename__ = "event_queue"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(String, unique=True, index=True)
    user_id = Column(String, index=True)
    payload = Column(JSON)
    status = Column(String, default="PENDING")

    attempts = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)

