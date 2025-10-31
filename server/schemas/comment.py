from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, constr
from server.schemas.user import UserSafe


class CommentCreateRequest(BaseModel):
    content: constr(min_length=1, max_length=5000)


class CommentUpdateRequest(BaseModel):
    content: constr(min_length=1, max_length=5000)


class CommentOut(BaseModel):
    id: int
    listing_id: int
    content: str
    created_at: datetime
    updated_at: datetime
    author: UserSafe
    is_owner: bool

    class Config:
        orm_mode = True


class CommentListResponse(BaseModel):
    items: List[CommentOut]
