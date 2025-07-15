from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from auth import schemas, services
from database.db_connection import get_db

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/signup", response_model=schemas.Users)
def signup(user: schemas.UsersCreate, db: Session = Depends(get_db)):
    """
    Register a new user with mobile number and optional information
    """
    try:
        db_user = services.create_user(db=db, user=user)
        return db_user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/send-otp", response_model=schemas.OTPResponse)
def send_otp(otp_request: schemas.OTPRequest, db: Session = Depends(get_db)):
    """
    Send OTP to user's mobile number (mocked, returned in response)
    """
    try:
        result = services.send_otp(db=db, phone=otp_request.phone)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/verify-otp", response_model=schemas.JWTTokenResponse)
def verify_otp(otp_verify_request: schemas.OTPVerifyRequest, db: Session = Depends(get_db)):
    """
    Verify OTP and return JWT token for session
    """
    try:
        result = services.verify_otp(db=db, phone=otp_verify_request.phone, otp=otp_verify_request.otp)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
