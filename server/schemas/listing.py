from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, AnyUrl, ConfigDict


class ListingIngestRequest(BaseModel):
    url: AnyUrl


class ListingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    url: str
    title: str
    image_url: Optional[str] = None
    view_count: int
    created_at: datetime


class ListingSingleResponse(BaseModel):
    listing: ListingOut


class ListingListResponse(BaseModel):
    items: List[ListingOut]
    total: int
