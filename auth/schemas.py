from datetime import datetime

from pydantic import BaseModel


class UsersBase(BaseModel):
    phone: str


class UsersCreate(UsersBase):
    pass


class Users(UsersBase):
    id: int

    class Config:
        from_attributes = True


class OTPRequest(BaseModel):
    phone: str


class OTPResponse(BaseModel):
    otp: str
    message: str


class OTPBase(BaseModel):
    phone: str
    otp: str
    created_at: datetime
    expired_at: datetime


class OTP(OTPBase):
    id: int

    class Config:
        from_attributes = True
