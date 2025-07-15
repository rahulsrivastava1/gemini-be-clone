import os
import random
from datetime import datetime, timedelta
from typing import Optional

import jwt
from sqlalchemy.orm import Session

from auth.models import OTP, Users
from auth.schemas import UsersCreate

# JWT Configuration (in production, these should be in environment variables)
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")


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


def verify_otp(db: Session, phone: str, otp: str):
    """
    Verify OTP and return JWT token if valid
    """
    # Get the latest OTP for the phone number (descending order by id)
    latest_otp = db.query(OTP).filter(OTP.phone == phone).order_by(OTP.id.desc()).first()

    if not latest_otp:
        raise ValueError("No OTP found for this phone number")

        # Check if OTP has expired
    if latest_otp.expired_at and datetime.now() > latest_otp.expired_at:
        raise ValueError("OTP has expired")

    # Verify OTP
    if str(latest_otp.otp) != str(otp):
        raise ValueError("Invalid OTP")

    # Invalidate OTP by setting expired_at to 5 minutes before current time
    latest_otp.expired_at = datetime.now() - timedelta(minutes=5)
    db.commit()

    # Get user details
    user = db.query(Users).filter(Users.phone == phone).first()
    if not user:
        raise ValueError("User not found")

    # Generate JWT token
    access_token = create_access_token(data={"sub": str(user.id), "phone": user.phone})

    return {"access_token": access_token, "token_type": "bearer", "message": "OTP verified successfully"}


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Create JWT access token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=float(ACCESS_TOKEN_EXPIRE_MINUTES))

    print("expire", expire)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str):
    """
    Verify JWT token and return payload
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")
