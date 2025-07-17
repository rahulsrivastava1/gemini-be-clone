from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from auth.models import Users
from database.db_connection import get_db
from middleware.dependencies import get_current_user

from . import schemas, services
from .models import Message
from .schemas import MessageCreate, MessageResponse
from .services import enqueue_message_for_gemini

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


@router.get("/chatroom", response_model=schemas.ChatroomListResponse)
def get_chatrooms(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all chatrooms for the authenticated user with caching"""
    phone = current_user["phone"]
    user = db.query(Users).filter(Users.phone == phone).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    chatrooms = services.get_user_chatrooms(db, user_id=user.id)

    return schemas.ChatroomListResponse(chatrooms=chatrooms, total_count=len(chatrooms))


@router.get("/chatroom/{chatroom_id}", response_model=schemas.ChatroomResponse)
def get_chatroom(chatroom_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    """Get detailed information about a specific chatroom"""
    phone = current_user["phone"]
    user = db.query(Users).filter(Users.phone == phone).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    try:
        chatroom = services.get_chatroom_by_id(db, chatroom_id=chatroom_id, user_id=user.id)
        return chatroom
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chatroom not found or access denied")


@router.post("/chatroom/{chatroom_id}/message", response_model=MessageResponse)
def send_message(
    chatroom_id: int, message: MessageCreate, current_user=Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Send a message to a chatroom and queue Gemini API call.
    """
    phone = current_user["phone"]
    user = db.query(Users).filter(Users.phone == phone).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Check chatroom ownership
    chatroom = db.query(services.Chatroom).filter_by(id=chatroom_id, user_id=user.id).first()
    if not chatroom:
        raise HTTPException(status_code=404, detail="Chatroom not found or access denied")

    # Create message (status pending)
    db_message = Message(user_id=user.id, chatroom_id=chatroom_id, content=message.content, status="pending")
    db.add(db_message)
    db.commit()
    db.refresh(db_message)

    # Queue Gemini API call
    enqueue_message_for_gemini(db_message.id)

    return db_message
