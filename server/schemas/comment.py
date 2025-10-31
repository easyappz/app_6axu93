from datetime import datetime
from pydantic import BaseModel, Field
from server.schemas.user import UserPublic


class CommentCreate(BaseModel):
    content: str = Field(min_length=1, max_length=5000)


class CommentUpdate(BaseModel):
    content: str = Field(min_length=1, max_length=5000)


class CommentOut(BaseModel):
    id: int
    listing_id: int
    content: str
    created_at: datetime
    updated_at: datetime
    author: UserPublic
    is_owner: bool

    class Config:
        from_attributes = True
