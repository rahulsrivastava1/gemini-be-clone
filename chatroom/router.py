from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from auth.models import Users
from database.db_connection import get_db
from middleware.dependencies import get_current_user

from . import schemas, services

router = APIRouter()


@router.post("/chatroom", response_model=schemas.ChatroomResponse)
def create_chatroom(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    phone = current_user["phone"]
    print("phone", phone)
    user = db.query(Users).filter(Users.phone == phone).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    chatroom = services.create_chatroom(db, user_id=user.id)
    return chatroom
