from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from auth import schemas, services
from auth.models import Users
from database.db_connection import get_db
from middleware.dependencies import get_current_user

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


@router.post("/forgot-password", response_model=schemas.OTPResponse)
def forgot_password(forgot_request: schemas.ForgotPasswordRequest, db: Session = Depends(get_db)):
    """
    Send OTP for password reset. First checks if user exists, then generates and stores OTP.
    """
    try:
        result = services.send_otp(db=db, phone=forgot_request.phone)
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


@router.post("/change-password", response_model=schemas.ChangePasswordResponse)
def change_password(
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Change password by generating new access token for authenticated user
    """
    try:
        result = services.change_password(db=db, user=current_user)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


user_router = APIRouter()


@user_router.get("/user/me", response_model=schemas.Users)
def read_current_user(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Get details about the currently authenticated user.
    """
    user = db.query(Users).filter(Users.phone == current_user["phone"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
