from fastapi import APIRouter

from app.core.dependencies import AdminUser, AgentOrAdmin, CurrentUser, DbDep
from app.modules.requests.repository import RequestsRepository
from app.modules.requests.schemas import (
    ApprovalDecision,
    ApprovalOut,
    CommentCreate,
    CommentOut,
    HistoryOut,
    RequestCreate,
    RequestListOut,
    RequestOut,
    RequestUpdate,
    SlaCreate,
    SlaOut,
    StatusUpdate,
)
from app.modules.requests.service import RequestsService

router = APIRouter(prefix="/requests", tags=["requests"])


def _service(db) -> RequestsService:
    return RequestsService(RequestsRepository(db), db)


# --- Requests CRUD ---


@router.post("/", response_model=RequestOut, status_code=201)
async def create_request(payload: RequestCreate, user: CurrentUser, db: DbDep):
    return await _service(db).create(user, payload)


@router.get("/", response_model=list[RequestListOut])
async def list_requests(user: CurrentUser, db: DbDep):
    return await _service(db).list_requests(user)


@router.get("/{request_id}", response_model=RequestOut)
async def get_request(request_id: int, user: CurrentUser, db: DbDep):
    return await _service(db).get(request_id, user)


@router.patch("/{request_id}", response_model=RequestOut)
async def classify_request(
    request_id: int, payload: RequestUpdate, user: AgentOrAdmin, db: DbDep
):
    return await _service(db).classify(request_id, user, payload)


@router.patch("/{request_id}/status", response_model=RequestOut)
async def change_status(
    request_id: int, payload: StatusUpdate, user: AgentOrAdmin, db: DbDep
):
    return await _service(db).change_status(request_id, user, payload)


# --- Comments ---


@router.post("/{request_id}/comments", response_model=CommentOut, status_code=201)
async def add_comment(
    request_id: int, payload: CommentCreate, user: CurrentUser, db: DbDep
):
    return await _service(db).add_comment(request_id, user, payload)


@router.get("/{request_id}/comments", response_model=list[CommentOut])
async def list_comments(request_id: int, user: CurrentUser, db: DbDep):
    return await _service(db).list_comments(request_id, user)


# --- History ---


@router.get("/{request_id}/history", response_model=list[HistoryOut])
async def list_history(request_id: int, user: AgentOrAdmin, db: DbDep):
    return await _service(db).list_history(request_id)


# --- SLA ---


@router.get("/{request_id}/sla", response_model=SlaOut)
async def get_sla(request_id: int, user: AgentOrAdmin, db: DbDep):
    return await _service(db).get_sla(request_id)


@router.put("/{request_id}/sla", response_model=SlaOut)
async def upsert_sla(
    request_id: int, payload: SlaCreate, user: AgentOrAdmin, db: DbDep
):
    return await _service(db).upsert_sla(request_id, user, payload)


# --- Approvals ---


@router.get("/{request_id}/approvals", response_model=list[ApprovalOut])
async def list_approvals(request_id: int, user: AgentOrAdmin, db: DbDep):
    return await _service(db).list_approvals(request_id)


@router.patch(
    "/{request_id}/approvals/{approval_id}", response_model=ApprovalOut
)
async def decide_approval(
    request_id: int,
    approval_id: int,
    payload: ApprovalDecision,
    user: AdminUser,
    db: DbDep,
):
    return await _service(db).decide_approval(
        request_id, approval_id, user, payload
    )
