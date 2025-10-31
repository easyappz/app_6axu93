from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class AuthorOut(BaseModel):
    id: int
    email: str
    name: Optional[str] = None


class CommentCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000)


class CommentUpdate(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000)


class CommentOut(BaseModel):
    id: int
    listing_id: int
    content: str
    created_at: datetime
    updated_at: datetime
    author: AuthorOut
    is_owner: bool

    class Config:
        orm_mode = True


class CommentsListResponse(BaseModel):
    items: List[CommentOut]
