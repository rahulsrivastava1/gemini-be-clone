from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from auth.models import Users
from database.db_connection import get_db
from middleware.dependencies import get_current_user

from . import schemas, services
from .models import Message
from .schemas import MessageCreate, MessageResponse

router = APIRouter()


@router.post("/chatroom", response_model=schemas.ChatroomResponse)
def create_chatroom(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    phone = current_user["phone"]
    print("phone", phone)
    user = db.query(Users).filter(Users.phone == phone).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    chatroom = services.create_chatroom(db, user_id=int(user.id))
    return chatroom


@router.get("/chatroom", response_model=schemas.ChatroomListResponse)
def get_chatrooms(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all chatrooms for the authenticated user with caching"""
    phone = current_user["phone"]
    user = db.query(Users).filter(Users.phone == phone).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    chatrooms = services.get_user_chatrooms(db, user_id=int(user.id))

    return schemas.ChatroomListResponse(chatrooms=chatrooms, total_count=len(chatrooms))


@router.get("/chatroom/{chatroom_id}", response_model=schemas.ChatroomResponse)
def get_chatroom(chatroom_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    """Get detailed information about a specific chatroom"""
    phone = current_user["phone"]
    user = db.query(Users).filter(Users.phone == phone).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    try:
        chatroom = services.get_chatroom_by_id(db, chatroom_id=chatroom_id, user_id=int(user.id))
        return chatroom
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chatroom not found or access denied")


@router.post("/chatroom/{chatroom_id}/message", response_model=MessageResponse)
def send_message(
    chatroom_id: int, message: MessageCreate, current_user=Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Send a message to a chatroom and process it asynchronously with Gemini API.
    """
    phone = current_user["phone"]
    user = db.query(Users).filter(Users.phone == phone).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Check chatroom ownership
    chatroom = db.query(services.Chatroom).filter_by(id=chatroom_id, user_id=user.id).first()
    if not chatroom:
        raise HTTPException(status_code=404, detail="Chatroom not found or access denied")

    # Save message and start async processing
    db_message = services.save_message_and_process_async(db, int(user.id), chatroom_id, message.content)

    return db_message
