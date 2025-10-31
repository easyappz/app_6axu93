from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from server.core.security import get_current_user
from server.db.database import get_db
from server.models.comment import Comment
from server.models.user import User
from server.schemas.comment import CommentOut, CommentUpdate

router = APIRouter(prefix="/comments", tags=["comments"])


@router.patch("/{comment_id}", response_model=dict)
def update_comment(
    comment_id: int,
    payload: CommentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    if comment.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can edit only your own comments")

    comment.content = payload.content
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
        author={
            "id": current_user.id,
            "email": current_user.email,
            "name": current_user.name,
            "created_at": current_user.created_at,
        },
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
