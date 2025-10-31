from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from server.db.database import get_db
from server.models.user import User
from server.schemas.auth import RegisterRequest, LoginRequest, AuthResponse
from server.schemas.user import UserSafe, UserMe
from server.core.security import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = User(email=data.email, name=data.name, password_hash=hash_password(data.password))
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(subject=str(user.id))
    return AuthResponse(user=UserSafe.from_orm(user), token=token)


@router.post("/login", response_model=AuthResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    token = create_access_token(subject=str(user.id))
    return AuthResponse(user=UserSafe.from_orm(user), token=token)


@router.get("/me", response_model=UserMe)
def me(current_user: User = Depends(get_current_user)):
    return UserMe.from_orm(current_user)
