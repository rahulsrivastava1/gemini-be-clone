from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class ChatroomCreate(BaseModel):
    user_id: int


class ChatroomResponse(BaseModel):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ChatroomListResponse(BaseModel):
    chatrooms: List[ChatroomResponse]
    total_count: int

    class Config:
        from_attributes = True


class MessageCreate(BaseModel):
    content: str


class MessageResponse(BaseModel):
    id: int
    user_id: int
    chatroom_id: int
    content: str
    response: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MessageListResponse(BaseModel):
    messages: List[MessageResponse]
    total_count: int

    class Config:
        from_attributes = True
