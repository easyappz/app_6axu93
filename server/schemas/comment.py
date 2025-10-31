from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class AuthorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    name: Optional[str] = None


class CommentCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000)


class CommentUpdate(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000)


class CommentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    listing_id: int
    content: str
    created_at: datetime
    updated_at: datetime
    author: AuthorOut
    is_owner: bool


class CommentsListResponse(BaseModel):
    items: List[CommentOut]
