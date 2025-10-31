from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from server.db.database import get_db
from server.models.comment import Comment
from server.models.user import User
from server.schemas.comment import CommentUpdateRequest, CommentOut
from server.core.security import get_current_user

router = APIRouter(prefix="/comments", tags=["Comments"])


@router.patch("/{comment_id}", response_model=dict)
def update_comment(
    comment_id: int,
    data: CommentUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    comment = db.query(Comment).options(joinedload(Comment.author)).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    if comment.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can edit only your own comments")

    comment.content = data.content
    # updated_at is managed as now
    from datetime import datetime

    comment.updated_at = datetime.utcnow()
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


@router.delete("/{comment_id}", response_model=dict)
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    if comment.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can delete only your own comments")

    db.delete(comment)
    db.commit()
    return {"success": True}
