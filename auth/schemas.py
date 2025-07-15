from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class UsersBase(BaseModel):
    phone: str


class UsersCreate(UsersBase):
    pass


class Users(UsersBase):
    id: int

    class Config:
        from_attributes = True


class OTPBase(BaseModel):
    phone: str
    otp: str
    created_at: datetime
    expired_at: datetime


class OTPCreate(OTPBase):
    pass


class OTP(OTPBase):
    id: int

    class Config:
        from_attributes = True
