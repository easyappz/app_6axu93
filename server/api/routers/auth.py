from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from server.db.database import get_db
from server.models.user import User
from server.schemas.user import UserCreate, UserLogin, UserOut, UserMe
from server.schemas.auth import AuthResponse
from server.core.security import get_password_hash, verify_password, create_access_token, get_current_user

router = APIRouter(tags=["auth"])  # no global prefix; paths are fully qualified below


@router.post("/auth/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    if len(payload.password) < 6:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password too short (min 6)")
    user = User(
        email=payload.email,
        name=payload.name,
        password_hash=get_password_hash(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(str(user.id))
    return AuthResponse(user=UserOut.model_validate(user), token=token)


@router.post("/auth/login", response_model=AuthResponse)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token(str(user.id))
    return AuthResponse(user=UserOut.model_validate(user), token=token)


@router.get("/auth/me", response_model=UserMe)
def me(current_user: User = Depends(get_current_user)):
    return current_user
