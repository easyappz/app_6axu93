from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, AnyUrl


class ListingIngestRequest(BaseModel):
    url: AnyUrl


class ListingOut(BaseModel):
    id: int
    url: str
    title: str
    image_url: Optional[str] = None
    view_count: int
    created_at: datetime

    class Config:
        orm_mode = True


class ListingListResponse(BaseModel):
    items: List[ListingOut]
    total: int
