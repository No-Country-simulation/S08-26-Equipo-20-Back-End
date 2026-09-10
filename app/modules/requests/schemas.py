from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.modules.requests.model import ApprovalStatus, RequestStatus


# --- Brief schemas for nested responses ---

class UserBrief(BaseModel):
    id: int
    name: str
    email: str

    model_config = ConfigDict(from_attributes=True)


class CategoryBrief(BaseModel):
    id: int
    name: str
    requires_approval: bool

    model_config = ConfigDict(from_attributes=True)


class PriorityBrief(BaseModel):
    id: int
    name: str
    level: int

    model_config = ConfigDict(from_attributes=True)


class TeamBrief(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


# --- Request schemas ---

class RequestCreate(BaseModel):
    description: str = Field(min_length=1)


class RequestUpdate(BaseModel):
    category_id: int | None = None
    priority_id: int | None = None
    team_id: int | None = None
    assigned_to: int | None = None


class StatusUpdate(BaseModel):
    status: RequestStatus


class RequestOut(BaseModel):
    id: int
    description: str
    status: RequestStatus
    category: CategoryBrief | None
    priority: PriorityBrief | None
    team: TeamBrief | None
    creator: UserBrief
    assignee: UserBrief | None
    resolved_at: datetime | None
    closed_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RequestListOut(BaseModel):
    id: int
    description: str
    status: RequestStatus
    category: CategoryBrief | None
    priority: PriorityBrief | None
    assignee: UserBrief | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Comment schemas ---

class CommentCreate(BaseModel):
    content: str = Field(min_length=1)
    is_internal: bool = False


class CommentOut(BaseModel):
    id: int
    content: str
    is_internal: bool
    user: UserBrief
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- History schemas ---

class HistoryOut(BaseModel):
    id: int
    action: str
    old_value: str | None
    new_value: str | None
    user: UserBrief
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- SLA schemas ---

class SlaCreate(BaseModel):
    response_deadline: datetime | None = None
    resolution_deadline: datetime | None = None


class SlaOut(BaseModel):
    id: int
    response_deadline: datetime | None
    resolution_deadline: datetime | None
    responded_at: datetime | None
    resolved_at: datetime | None
    response_on_time: bool | None = None
    resolution_on_time: bool | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Approval schemas ---

class ApprovalOut(BaseModel):
    id: int
    status: ApprovalStatus
    comment: str | None
    approver: UserBrief
    created_at: datetime
    decided_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class ApprovalDecision(BaseModel):
    status: ApprovalStatus
    comment: str | None = None
