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
    created_at: str

    model_config = {
        "from_attributes": True
    }


class ListingListResponse(BaseModel):
    items: List[ListingOut]
    total: int
