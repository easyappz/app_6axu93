from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from server.db.database import get_db
from server.models.listing import Listing
from server.models.comment import Comment
from server.models.user import User
from server.schemas.listing import ListingIngestRequest, ListingOut, ListingListResponse
from server.schemas.comment import CommentCreateRequest, CommentListResponse, CommentOut
from server.core.security import get_current_user, get_optional_user
from server.services.avito_scraper import fetch_html, parse_title_and_image, download_image

router = APIRouter(prefix="/listings", tags=["Listings"])


MEDIA_PREFIX = "/media/"


def to_listing_out(model: Listing) -> ListingOut:
    image_url = None
    if model.image_path:
        image_url = f"{MEDIA_PREFIX}{model.image_path}"
    return ListingOut(
        id=model.id,
        url=model.url,
        title=model.title,
        image_url=image_url,
        view_count=model.view_count,
        created_at=model.created_at,
    )


@router.post("/ingest", response_model=dict, status_code=status.HTTP_201_CREATED)
def ingest_listing(payload: ListingIngestRequest, db: Session = Depends(get_db)):
    existing = db.query(Listing).filter(Listing.url == str(payload.url)).first()
    if existing:
        # Return existing
        return {"listing": to_listing_out(existing)}

    html = fetch_html(str(payload.url))
    title, image_url = parse_title_and_image(html)
    if not title:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to parse listing title from the provided URL")

    image_path: Optional[str] = None
    if image_url:
        try:
            image_path = download_image(image_url)
        except Exception:
            # Image is optional, continue without it
            image_path = None

    listing = Listing(url=str(payload.url), title=title, image_path=image_path)
    db.add(listing)
    db.commit()
    db.refresh(listing)

    return {"listing": to_listing_out(listing)}


@router.get("", response_model=ListingListResponse)
def list_listings(
    db: Session = Depends(get_db),
    sort: str = Query("views", description="Sort by 'views' only"),
    limit: int = Query(10, ge=1, le=100),
):
    q = db.query(Listing)
    if sort == "views":
        q = q.order_by(Listing.view_count.desc())
    total = q.count()
    items = q.limit(limit).all()
    return ListingListResponse(items=[to_listing_out(i) for i in items], total=total)


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


@router.get("/{listing_id}/comments", response_model=CommentListResponse)
def list_comments(
    listing_id: int,
    db: Session = Depends(get_db),
    maybe_user: Optional[User] = Depends(get_optional_user),
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

    def to_comment_out(c: Comment) -> CommentOut:
        is_owner = maybe_user is not None and c.user_id == maybe_user.id
        return CommentOut(
            id=c.id,
            listing_id=c.listing_id,
            content=c.content,
            created_at=c.created_at,
            updated_at=c.updated_at,
            author={
                "id": c.author.id,
                "email": c.author.email,
                "name": c.author.name,
            },
            is_owner=is_owner,
        )

    return CommentListResponse(items=[to_comment_out(c) for c in comments])


@router.post("/{listing_id}/comments", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_comment(
    listing_id: int,
    data: CommentCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")

    comment = Comment(listing_id=listing_id, user_id=current_user.id, content=data.content)
    db.add(comment)
    db.commit()
    db.refresh(comment)

    out = CommentOut(
        id=comment.id,
        listing_id=comment.listing_id,
        content=comment.content,
        created_at=comment.created_at,
        updated_at=comment.updated_at,
        author={"id": current_user.id, "email": current_user.email, "name": current_user.name},
        is_owner=True,
    )
    return {"comment": out}
