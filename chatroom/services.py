from sqlalchemy.orm import Session

from .models import Chatroom


def create_chatroom(db: Session, user_id: int) -> Chatroom:
    chatroom = Chatroom(user_id=user_id)
    db.add(chatroom)
    db.commit()
    db.refresh(chatroom)
    return chatroom
