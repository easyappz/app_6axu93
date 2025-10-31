from datetime import datetime
from pydantic import BaseModel, AnyHttpUrl


class ListingOut(BaseModel):
    id: int
    url: AnyHttpUrl | str
    title: str
    image_url: str | None = None
    view_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class ListingIngestRequest(BaseModel):
    url: AnyHttpUrl | str


class ListingsListResponse(BaseModel):
    items: list[ListingOut]
    total: int
