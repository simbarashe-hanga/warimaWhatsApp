from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db import SessionLocal
from app.models import User, Contribution, Group

def get_db():
    return SessionLocal()

def get_or_create_user(db: Session, phone: str) -> User:
    db = get_db()

    try:
        user = db.query(User).filter_by(phone=phone).first()

        if not user:
            user = User(phone=phone)
            db.add(user)
            db.commit()
            db.refresh(user)

        return user

    finally:
        db.close()


def record_contribution(db: Session, phone: str, amount: float):
    user = get_or_create_user(db, phone)

    contribution = Contribution(
        user_id=user.id,
        amount=amount
    )

    db.add(contribution)
    db.commit()
    db.refresh(contribution)

    return contribution


def get_balance(db: Session, phone: str):
    db = get_db()

    try:
        user = db.query(User).filter_by(phone=phone).first()

        if not user:
            return 0.0

        total = db.query(func.sum(Contribution.amount))\
            .filter(Contribution.user_id == user.id)\
            .scalar()

        return float(total or 0.0)

    finally:
        db.close()


def get_group_balance(group_id: int) -> float:
    db = get_db()

    try:
        total = db.query(func.sum(Contribution.amount))\
            .filter(Contribution.group_id == group_id)\
            .scalar()

        return float(total or 0.0)

    finally:
        db.close()
