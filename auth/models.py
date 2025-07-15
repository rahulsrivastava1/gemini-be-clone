from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from database.db_connection import Base


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String, index=True)


class OTP(Base):
    __tablename__ = "otp"

    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String, index=True)
    otp = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.now)
    expired_at = Column(DateTime)
