from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class UserBase(BaseModel):
    login: str


# Query models
class CreateUser(UserBase):
    password: str


class UpdateUser(UserBase):
    id: int


class LoginUser(UserBase):
    password: str


# Response models
class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


# Token
# Response for user
class Token(BaseModel):
    access_token: str
    token_type: str


# User sending token
class TokenData(BaseModel):
    username: Optional[str] = None
