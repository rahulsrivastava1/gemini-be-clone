from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text

from auth.models import Users
from database.db_connection import Base


class Chatroom(Base):
    __tablename__ = "chatroom"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey(Users.id), nullable=False)
    created_at = Column(DateTime, default=datetime.now)


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey(Users.id), nullable=False)
    chatroom_id = Column(Integer, ForeignKey(Chatroom.id), nullable=False)
    content = Column(Text, nullable=False)
    response = Column(Text, nullable=True)  # Gemini API response
    status = Column(String(20), default="pending")  # pending, processing, completed, failed
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
