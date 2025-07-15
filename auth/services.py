import random
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from auth.models import OTP, Users
from auth.schemas import UsersCreate


def create_user(db: Session, user: UsersCreate):
    """
    Create a new user with the provided information
    """
    # Check if user with this phone number already exists
    existing_user = db.query(Users).filter(Users.phone == user.phone).first()
    if existing_user:
        raise ValueError("User with this phone number already exists")

    # Create new user
    db_user = Users(phone=user.phone)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


def send_otp(db: Session, phone: str):
    """
    Send OTP to user's mobile number
    """
    # Check if user exists with this phone number
    existing_user = db.query(Users).filter(Users.phone == phone).first()
    if not existing_user:
        raise ValueError("User with this phone number does not exist")

    # Generate 4-digit OTP
    otp_code = str(random.randint(1000, 9999))

    # Set expiration time (5 minutes from now)
    created_at = datetime.now()
    expired_at = created_at + timedelta(minutes=5)

    # Create OTP record
    db_otp = OTP(phone=phone, otp=otp_code, created_at=created_at, expired_at=expired_at)

    db.add(db_otp)
    db.commit()
    db.refresh(db_otp)

    return {"otp": otp_code, "message": "OTP sent successfully"}
