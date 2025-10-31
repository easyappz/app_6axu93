from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserPublic(BaseModel):
    id: int
    email: EmailStr
    name: Optional[str] = None
    created_at: Optional[str] = Field(default=None, description="ISO datetime")

    model_config = {
        "from_attributes": True
    }
