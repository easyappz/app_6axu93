from datetime import datetime
from pydantic import BaseModel, EmailStr


class UserPublic(BaseModel):
    id: int
    email: EmailStr
    name: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True
