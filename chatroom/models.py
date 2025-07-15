from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer

from auth.models import Users
from database.db_connection import Base


class Chatroom(Base):
    __tablename__ = "chatroom"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey(Users.id), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
