from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional


class UserSafe(BaseModel):
    id: int
    email: EmailStr
    name: Optional[str] = None

    class Config:
        orm_mode = True


class UserMe(BaseModel):
    id: int
    email: EmailStr
    name: Optional[str] = None
    created_at: datetime

    class Config:
        orm_mode = True
