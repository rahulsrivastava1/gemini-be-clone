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
