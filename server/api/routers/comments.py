from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from server.db.database import get_db
from server.models.comment import Comment
from server.models.user import User
from server.schemas.comment import CommentUpdate, CommentOut, AuthorOut
from server.core.security import get_current_user

router = APIRouter(prefix="/comments", tags=["comments"])


def to_comment_out(comment: Comment, current_user: User) -> CommentOut:
    return CommentOut(
        id=comment.id,
        listing_id=comment.listing_id,
        content=comment.content,
        created_at=comment.created_at,
        updated_at=comment.updated_at,
        author=AuthorOut(id=comment.author.id, email=comment.author.email, name=comment.author.name),
        is_owner=(current_user.id == comment.user_id),
    )


@router.patch("/{comment_id}", response_model=dict)
def update_comment(
    comment_id: int,
    payload: CommentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    if comment.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not the author of this comment")
    new_content = payload.content.strip()
    if not new_content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Content cannot be empty")
    comment.content = new_content
    db.commit()
    db.refresh(comment)
    return {"comment": to_comment_out(comment, current_user)}


@router.delete("/{comment_id}", response_model=dict, status_code=status.HTTP_200_OK)
def delete_comment(
    comment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    if comment.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not the author of this comment")
    db.delete(comment)
    db.commit()
    return {"success": True}
