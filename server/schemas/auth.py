from pydantic import BaseModel, EmailStr, constr
from typing import Optional
from server.schemas.user import UserSafe


class RegisterRequest(BaseModel):
    email: EmailStr
    password: constr(min_length=6)
    name: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: constr(min_length=6)


class AuthResponse(BaseModel):
    user: UserSafe
    token: str
