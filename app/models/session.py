from sqlalchemy import Column, String, JSON
from app.db.base import Base


class UserSession(Base):
    __tablename__ = "user_sessions"

    user_id = Column(String, primary_key=True)
    state = Column(String)
    context = Column(JSON)
