from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from requests import RequestException

from server.db.database import get_db
from server.models.listing import Listing
from server.models.comment import Comment
from server.models.user import User
from server.schemas.listing import (
    ListingIngestRequest,
    ListingOut,
    ListingListResponse,
    ListingSingleResponse,
)
from server.schemas.comment import CommentCreate, CommentOut, CommentsListResponse, AuthorOut
from server.core.security import get_current_user, get_optional_user
from server.services.avito_scraper import fetch_html, parse_title_and_image, download_image

router = APIRouter(tags=["listings"])  # no global prefix; paths are fully qualified below


def to_listing_out(listing: Listing) -> ListingOut:
    image_url = f"/media/{listing.image_path}" if listing.image_path else None
    return ListingOut(
        id=listing.id,
        url=listing.url,
        title=listing.title,
        image_url=image_url,
        view_count=listing.view_count,
        created_at=listing.created_at,
    )


def to_comment_out(comment: Comment, current_user: Optional[User]) -> CommentOut:
    return CommentOut(
        id=comment.id,
        listing_id=comment.listing_id,
        content=comment.content,
        created_at=comment.created_at,
        updated_at=comment.updated_at,
        author=AuthorOut(id=comment.author.id, email=comment.author.email, name=comment.author.name),
        is_owner=(current_user.id == comment.user_id) if current_user else False,
    )


@router.post("/listings/ingest", response_model=ListingSingleResponse, status_code=status.HTTP_200_OK)
def ingest_listing(payload: ListingIngestRequest, db: Session = Depends(get_db)):
    # Return existing if already ingested
    existing = db.query(Listing).filter(Listing.url == str(payload.url)).first()
    if existing:
        return ListingSingleResponse(listing=to_listing_out(existing))

    # Fetch and parse
    try:
        html = fetch_html(str(payload.url))
    except RequestException:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to fetch the URL")

    title, image_url = parse_title_and_image(html)
    if not title:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to parse listing title")

    image_path: Optional[str] = None
    if image_url:
        try:
            image_path = download_image(image_url)
        except Exception:
            image_path = None  # Only images are saved locally; ignore failures

    listing = Listing(url=str(payload.url), title=title, image_path=image_path)
    db.add(listing)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        # In case of race, return the existing row
        existing = db.query(Listing).filter(Listing.url == str(payload.url)).first()
        if existing:
            return ListingSingleResponse(listing=to_listing_out(existing))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Could not create listing")

    db.refresh(listing)
    return ListingSingleResponse(listing=to_listing_out(listing))


@router.get("/listings", response_model=ListingListResponse)
def list_listings(
    sort: str = Query("views", pattern="^views$"),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    q = db.query(Listing)
    total = q.count()
    if sort == "views":
        q = q.order_by(Listing.view_count.desc())
    items = q.limit(limit).all()
    return ListingListResponse(items=[to_listing_out(x) for x in items], total=total)


@router.get("/listings/{listing_id}", response_model=ListingSingleResponse)
def get_listing(listing_id: int, db: Session = Depends(get_db)):
    # Atomic increment via DB update
    updated = (
        db.query(Listing)
        .filter(Listing.id == listing_id)
        .update({Listing.view_count: Listing.view_count + 1}, synchronize_session=False)
    )
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")
    db.commit()
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    return ListingSingleResponse(listing=to_listing_out(listing))


@router.get("/listings/{listing_id}/comments", response_model=CommentsListResponse)
def get_listing_comments(
    listing_id: int,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")
    comments = (
        db.query(Comment)
        .filter(Comment.listing_id == listing_id)
        .order_by(Comment.created_at.asc())
        .all()
    )
    return CommentsListResponse(items=[to_comment_out(c, current_user) for c in comments])


@router.post("/listings/{listing_id}/comments", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_comment(
    listing_id: int,
    payload: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")
    content = payload.content.strip()
    if not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Content cannot be empty")
    comment = Comment(listing_id=listing_id, user_id=current_user.id, content=content)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    out = {
        "comment": {
            "id": comment.id,
            "listing_id": comment.listing_id,
            "content": comment.content,
            "created_at": comment.created_at,
            "updated_at": comment.updated_at,
            "author": {"id": current_user.id, "email": current_user.email, "name": current_user.name},
            "is_owner": True,
        }
    }
    return out
