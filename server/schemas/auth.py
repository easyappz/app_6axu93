from pydantic import BaseModel
from server.schemas.user import UserOut


class AuthResponse(BaseModel):
    user: UserOut
    token: str
