from sqlalchemy import Column, String, Integer
from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    user_id = Column(String)
    user_name = Column(String)
    status = Column(String)
    balance = Column(Integer)
    message_id = Column(String)
