from pydantic import BaseModel, EmailStr, Field

from app.modules.users.schemas import UserResponse


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8)


__all__ = ["LoginRequest", "TokenResponse", "ChangePasswordRequest", "UserResponse"]