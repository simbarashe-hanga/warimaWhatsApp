from sqlalchemy import Column, String, Integer
from app.db.base import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String, primary_key=True)
    user_id = Column(String)
    amount = Column(Integer)
    status = Column(String)
    idempotency_key = Column(String, unique=True)
