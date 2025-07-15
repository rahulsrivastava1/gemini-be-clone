from datetime import datetime

from pydantic import BaseModel


class ChatroomCreate(BaseModel):
    user_id: int


class ChatroomResponse(BaseModel):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True
