from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CustomerBaseSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True,
    )


# --- Nested Support Schemas ---

class CategoryRead(CustomerBaseSchema):
    id: int
    name: str
    description: str | None = None


class PriorityRead(CustomerBaseSchema):
    id: int | None = None
    name: str
    level: int | None = None


class TeamRead(CustomerBaseSchema):
    id: int
    name: str
    description: str | None = None


class UserPublicRead(CustomerBaseSchema):
    id: int
    name: str
    email: str


class AttachmentRead(CustomerBaseSchema):
    id: int
    request_id: int
    uploaded_by: int
    file_name: str
    file_path: str
    created_at: datetime


class CommentRead(CustomerBaseSchema):
    id: int
    request_id: int
    user_id: int
    content: str
    is_internal: bool
    created_at: datetime
    user: UserPublicRead | None = None


# --- Target Customer Schemas ---

class CustomerRequestCreate(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    description: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="Detailed description of the customer request or issue",
        examples=["Al intentar abonar la factura con tarjeta corporativa, devuelve HTTP 500."],
    )

class CustomerRequestRead(CustomerBaseSchema):
    id: int
    description: str
    status: str
    category_id: int | None = None
    priority_id: int | None = None
    team_id: int | None = None
    created_by: int
    assigned_to: int | None = None
    created_at: datetime
    updated_at: datetime
    resolved_at: datetime | None = None
    closed_at: datetime | None = None


class CustomerRequestDetail(CustomerRequestRead):
    category: CategoryRead | None = None
    priority: PriorityRead | None = None
    team: TeamRead | None = None
    creator: UserPublicRead | None = None
    assignee: UserPublicRead | None = None
    comments: list[CommentRead] = Field(default_factory=list)
    attachments: list[AttachmentRead] = Field(default_factory=list)


class CommentCreate(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    content: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Text content of the comment",
        examples=["Probé con otra tarjeta de crédito y arrojó el mismo código de error."],
    )
