from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    phone = Column(String, unique=True)

    group_id = Column(Integer, ForeignKey("groups.id"))
    group = relationship("Group", back_populates="members")

    opt_in = Column(Boolean, default=False)


class Contribution(Base):
    __tablename__ = "contributions"

    id = Column(Integer, primary_key=True)
    amount = Column(Float)

    user_id = Column(Integer, ForeignKey("users.id"))
    group_id = Column(Integer, ForeignKey("groups.id"))


class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True)
    name = Column(String)

    members = relationship("User", back_populates="group")
