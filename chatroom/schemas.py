from datetime import datetime
from typing import List

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
