from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator


class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    role_id: int
    team_id: int | None = None
    password: str | None = Field(default=None, min_length=8, max_length=128)

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("El nombre no puede estar vacío")
        return value


class UserUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    role_id: int | None = None
    team_id: int | None = None
    is_active: bool | None = None


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    team: str | None
    role_id: int
    team_id: int | None
    must_change_password: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    @classmethod
    def flatten_relations(cls, data):
        if data is not None and not isinstance(data, dict):
            return {
                "id": data.id,
                "name": data.name,
                "email": data.email,
                "role": data.role.name,
                "team": data.team.name if data.team else None,
                "role_id": data.role_id,
                "team_id": data.team_id,
                "must_change_password": data.must_change_password,
                "is_active": data.is_active,
                "created_at": data.created_at,
                "updated_at": data.updated_at,
            }
        return data


class UserCreateResponse(BaseModel):
    user: UserResponse
    temporary_password: str | None = None


class UserList(BaseModel):
    items: list[UserResponse]
    total: int