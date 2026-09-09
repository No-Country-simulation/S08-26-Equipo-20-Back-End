from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8)


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    team: str | None
    must_change_password: bool
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    @classmethod
    def flatten_relations(cls, data):
        if data is not None and not isinstance(data, dict) and hasattr(data, "role"):
            return {
                "id": data.id,
                "name": data.name,
                "email": data.email,
                "role": data.role.name,
                "team": data.team.name if data.team else None,
                "must_change_password": data.must_change_password,
                "is_active": data.is_active,
                "created_at": data.created_at,
            }
        return data