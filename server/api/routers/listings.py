from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from server.core.security import get_current_user, get_optional_current_user
from server.db.database import get_db
from server.models.comment import Comment
from server.models.listing import Listing
from server.models.user import User
from server.schemas.comment import CommentCreate, CommentOut
from server.schemas.listing import ListingIngestRequest, ListingOut, ListingsListResponse
from server.services.avito_scraper import fetch_html, parse_title_and_image, download_image

router = APIRouter(prefix="/listings", tags=["listings"])


def build_image_url(image_path: Optional[str]) -> Optional[str]:
    if not image_path:
        return None
    return f"/media/{image_path}"


def to_listing_out(listing: Listing) -> ListingOut:
    return ListingOut(
        id=listing.id,
        url=listing.url,
        title=listing.title,
        image_url=build_image_url(listing.image_path),
        view_count=listing.view_count,
        created_at=listing.created_at,
    )


@router.post("/ingest", response_model=dict)
def ingest_listing(payload: ListingIngestRequest, db: Session = Depends(get_db)):
    url = payload.url.strip()
    existing = db.query(Listing).filter(Listing.url == url).first()
    if existing:
        return {"listing": to_listing_out(existing)}

    html = fetch_html(url)
    title, image_url = parse_title_and_image(html)

    if not title:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unable to parse listing title from the provided URL")

    image_path: Optional[str] = None
    if image_url:
        try:
            image_path = download_image(image_url)
        except Exception:
            image_path = None

    listing = Listing(url=url, title=title, image_path=image_path)
    db.add(listing)
    db.commit()
    db.refresh(listing)

    return {"listing": to_listing_out(listing)}


@router.get("", response_model=ListingsListResponse)
def list_listings(
    db: Session = Depends(get_db),
    sort: str = Query("views", pattern="^views$"),
    limit: int = Query(10, ge=1, le=100),
):
    query = db.query(Listing)
    if sort == "views":
        query = query.order_by(Listing.view_count.desc(), Listing.id.desc())

    items = query.limit(limit).all()
    total = db.query(func.count(Listing.id)).scalar() or 0

    return ListingsListResponse(items=[to_listing_out(it) for it in items], total=total)


@router.get("/{listing_id}", response_model=dict)
def get_listing_detail(listing_id: int, db: Session = Depends(get_db)):
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")

    listing.view_count += 1
    db.add(listing)
    db.commit()
    db.refresh(listing)

    return {"listing": to_listing_out(listing)}


@router.get("/{listing_id}/comments", response_model=dict)
def get_listing_comments(
    listing_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")

    comments = (
        db.query(Comment)
        .options(joinedload(Comment.author))
        .filter(Comment.listing_id == listing_id)
        .order_by(Comment.created_at.asc())
        .all()
    )

    items: list[CommentOut] = []
    for c in comments:
        items.append(
            CommentOut(
                id=c.id,
                listing_id=c.listing_id,
                content=c.content,
                created_at=c.created_at,
                updated_at=c.updated_at,
                author={
                    "id": c.author.id,
                    "email": c.author.email,
                    "name": c.author.name,
                    "created_at": c.author.created_at,
                },
                is_owner=(current_user.id == c.user_id) if current_user else False,
            )
        )

    return {"items": items}


@router.post("/{listing_id}/comments", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_comment(
    listing_id: int,
    payload: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")

    comment = Comment(listing_id=listing.id, user_id=current_user.id, content=payload.content)
    db.add(comment)
    db.commit()
    db.refresh(comment)

    out = CommentOut(
        id=comment.id,
        listing_id=comment.listing_id,
        content=comment.content,
        created_at=comment.created_at,
        updated_at=comment.updated_at,
        author={
            "id": current_user.id,
            "email": current_user.email,
            "name": current_user.name,
            "created_at": current_user.created_at,
        },
        is_owner=True,
    )
    return {"comment": out}
