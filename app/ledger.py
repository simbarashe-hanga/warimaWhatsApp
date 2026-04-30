from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db import SessionLocal
from app.models import User, Contribution, Group

def get_db():
    return SessionLocal()

def get_or_create_user(db: Session, phone: str) -> User:
    user = db.query(User).filter_by(phone=phone).first()

    if not user:
        user = User(phone=phone)
        db.add(user)
        db.commit()
        db.refresh(user)

    return user

def get_or_create_default_group(db):
    group = db.query(Group).filter_by(name="default").first()

    if not group:
        group = Group(name="default")
        db.add(group)
        db.flush()

    return group

def record_contribution(db: Session, user, amount: float, group_id: int):
    contribution = Contribution(
        user_id=user.id,
        amount=amount,
        group_id=group_id
    )

    db.add(contribution)
    return contribution


def get_balance(db: Session, phone: str):
    user = db.query(User).filter_by(phone=phone).first()

    if not user:
        return 0.0

    total = db.query(func.sum(Contribution.amount)) \
        .filter(Contribution.user_id == user.id) \
        .scalar()

    return float(total or 0.0)


def get_group_balance(db: Session, group_id: int) -> float:
    total = db.query(func.sum(Contribution.amount))\
        .filter(Contribution.group_id == group_id)\
        .scalar()

    return float(total or 0.0)
