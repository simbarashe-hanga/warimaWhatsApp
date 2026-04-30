from sqlalchemy import Column, String
from app.db.base import Base


class ProcessedMessage(Base):
    __tablename__ = "processed_messages"

    message_id = Column(String, primary_key=True)
