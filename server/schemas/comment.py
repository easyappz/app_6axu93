from typing import List
from pydantic import BaseModel, Field
from server.schemas.user import UserPublic


class CommentCreateRequest(BaseModel):
    content: str = Field(min_length=1, max_length=5000)


class CommentUpdateRequest(BaseModel):
    content: str = Field(min_length=1, max_length=5000)


class CommentOut(BaseModel):
    id: int
    listing_id: int
    content: str
    created_at: str
    updated_at: str
    author: UserPublic
    is_owner: bool

    model_config = {
        "from_attributes": True
    }


class CommentsListResponse(BaseModel):
    items: List[CommentOut]
