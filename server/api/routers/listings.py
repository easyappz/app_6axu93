from typing import Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from server.db.database import get_db
from server.models.listing import Listing
from server.models.comment import Comment
from server.models.user import User
from server.schemas.listing import ListingIngestRequest, ListingOut, ListingListResponse
from server.schemas.comment import CommentOut, CommentsListResponse
from server.schemas.user import UserPublic
from server.core.security import get_optional_user
from server.services.avito_scraper import fetch_html, parse_title_and_image, download_image

router = APIRouter()


MEDIA_PREFIX = "/media/"


def to_listing_out(m: Listing) -> ListingOut:
    image_url = None
    if m.image_path:
        image_url = f"{MEDIA_PREFIX}{m.image_path}"
    return ListingOut(
        id=m.id,
        url=m.url,
        title=m.title,
        image_url=image_url,
        view_count=m.view_count,
        created_at=m.created_at.isoformat(),
    )


def to_comment_out(c: Comment, current_user: Optional[User]) -> CommentOut:
    author_public = UserPublic(id=c.author.id, email=c.author.email, name=c.author.name, created_at=c.author.created_at.isoformat())
    is_owner = bool(current_user and current_user.id == c.user_id)
    return CommentOut(
        id=c.id,
        listing_id=c.listing_id,
        content=c.content,
        created_at=c.created_at.isoformat(),
        updated_at=c.updated_at.isoformat(),
        author=author_public,
        is_owner=is_owner,
    )


@router.post("/listings/ingest", response_model=ListingOut)
def ingest_listing(payload: ListingIngestRequest, db: Session = Depends(get_db)):
    existing = db.query(Listing).filter(func.lower(Listing.url) == func.lower(payload.url)).first()
    if existing:
        return to_listing_out(existing)

    try:
        html = fetch_html(payload.url)
        parsed = parse_title_and_image(html)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to fetch/parse URL: {e}")

    title = parsed.title
    image_path = None

    if parsed.image_url:
        try:
            image_path = download_image(parsed.image_url)
        except Exception:
            image_path = None

    listing = Listing(url=str(payload.url), title=title or "Untitled", image_path=image_path)
    db.add(listing)
    db.commit()
    db.refresh(listing)

    return to_listing_out(listing)


@router.get("/listings", response_model=ListingListResponse)
def list_listings(
    sort: str = Query("views", pattern="^(views|created)$"),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    q = db.query(Listing)
    total = q.count()
    if sort == "views":
        q = q.order_by(Listing.view_count.desc())
    else:
        q = q.order_by(Listing.created_at.desc())
    items = [to_listing_out(m) for m in q.limit(limit).all()]
    return ListingListResponse(items=items, total=total)


@router.get("/listings/{listing_id}", response_model=ListingOut)
def get_listing(listing_id: int, db: Session = Depends(get_db)):
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")
    # increment view count
    listing.view_count = int(listing.view_count or 0) + 1
    db.add(listing)
    db.commit()
    db.refresh(listing)
    return to_listing_out(listing)


@router.get("/listings/{listing_id}/comments", response_model=CommentsListResponse)
def get_listing_comments(
    listing_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")

    q = (
        db.query(Comment)
        .filter(Comment.listing_id == listing_id)
        .order_by(Comment.created_at.asc())
        .join(Comment.author)
    )
    comments = q.all()
    items = [to_comment_out(c, current_user) for c in comments]
    return CommentsListResponse(items=items)
