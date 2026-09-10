from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.requests.model import (
    Approval,
    ApprovalStatus,
    Comment,
    Request,
    RequestHistory,
    RequestStatus,
    Sla,
)


def _request_options():
    """Eager load options for Request queries."""
    return [
        selectinload(Request.category),
        selectinload(Request.priority),
        selectinload(Request.team),
        selectinload(Request.creator),
        selectinload(Request.assignee),
    ]


class RequestsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # --- Requests CRUD ---

    async def create(self, data: dict) -> Request:
        request = Request(**data)
        self.db.add(request)
        await self.db.commit()
        await self.db.refresh(request)
        return await self.get_by_id(request.id)

    async def get_by_id(self, request_id: int) -> Request | None:
        stmt = (
            select(Request)
            .options(*_request_options())
            .where(Request.id == request_id)
        )
        return await self.db.scalar(stmt)

    async def list_all(self) -> list[Request]:
        stmt = (
            select(Request)
            .options(*_request_options())
            .order_by(Request.created_at.desc())
        )
        result = await self.db.scalars(stmt)
        return list(result.all())

    async def list_by_creator(self, user_id: int) -> list[Request]:
        stmt = (
            select(Request)
            .options(*_request_options())
            .where(Request.created_by == user_id)
            .order_by(Request.created_at.desc())
        )
        result = await self.db.scalars(stmt)
        return list(result.all())

    async def update(self, request: Request, data: dict) -> Request:
        for key, value in data.items():
            setattr(request, key, value)
        await self.db.commit()
        await self.db.refresh(request)
        return await self.get_by_id(request.id)

    # --- History ---

    async def add_history(
        self,
        request_id: int,
        user_id: int,
        action: str,
        old_value: str | None = None,
        new_value: str | None = None,
    ) -> RequestHistory:
        entry = RequestHistory(
            request_id=request_id,
            user_id=user_id,
            action=action,
            old_value=old_value,
            new_value=new_value,
        )
        self.db.add(entry)
        await self.db.flush()
        return entry

    async def list_history(self, request_id: int) -> list[RequestHistory]:
        stmt = (
            select(RequestHistory)
            .options(selectinload(RequestHistory.user))
            .where(RequestHistory.request_id == request_id)
            .order_by(RequestHistory.created_at)
        )
        result = await self.db.scalars(stmt)
        return list(result.all())

    # --- Comments ---

    async def add_comment(
        self,
        request_id: int,
        user_id: int,
        content: str,
        is_internal: bool = False,
    ) -> Comment:
        comment = Comment(
            request_id=request_id,
            user_id=user_id,
            content=content,
            is_internal=is_internal,
        )
        self.db.add(comment)
        await self.db.commit()
        await self.db.refresh(comment)
        stmt = (
            select(Comment)
            .options(selectinload(Comment.user))
            .where(Comment.id == comment.id)
        )
        return await self.db.scalar(stmt)

    async def list_comments(
        self, request_id: int, include_internal: bool = True
    ) -> list[Comment]:
        stmt = (
            select(Comment)
            .options(selectinload(Comment.user))
            .where(Comment.request_id == request_id)
        )
        if not include_internal:
            stmt = stmt.where(Comment.is_internal == False)
        stmt = stmt.order_by(Comment.created_at)
        result = await self.db.scalars(stmt)
        return list(result.all())

    # --- SLA ---

    async def create_sla(self, request_id: int, data: dict) -> Sla:
        sla = Sla(request_id=request_id, **data)
        self.db.add(sla)
        await self.db.commit()
        await self.db.refresh(sla)
        return sla

    async def get_sla_by_request(self, request_id: int) -> Sla | None:
        stmt = select(Sla).where(Sla.request_id == request_id)
        return await self.db.scalar(stmt)

    async def update_sla(self, sla: Sla, data: dict) -> Sla:
        for key, value in data.items():
            setattr(sla, key, value)
        await self.db.commit()
        await self.db.refresh(sla)
        return sla

    # --- Approvals ---

    async def create_approval(
        self, request_id: int, approver_id: int
    ) -> Approval:
        approval = Approval(
            request_id=request_id,
            approver_id=approver_id,
            status=ApprovalStatus.PENDING,
        )
        self.db.add(approval)
        await self.db.commit()
        await self.db.refresh(approval)
        stmt = (
            select(Approval)
            .options(selectinload(Approval.approver))
            .where(Approval.id == approval.id)
        )
        return await self.db.scalar(stmt)

    async def list_approvals(self, request_id: int) -> list[Approval]:
        stmt = (
            select(Approval)
            .options(selectinload(Approval.approver))
            .where(Approval.request_id == request_id)
            .order_by(Approval.created_at)
        )
        result = await self.db.scalars(stmt)
        return list(result.all())

    async def get_approval(self, approval_id: int) -> Approval | None:
        stmt = (
            select(Approval)
            .options(selectinload(Approval.approver))
            .where(Approval.id == approval_id)
        )
        return await self.db.scalar(stmt)

    async def update_approval(self, approval: Approval, data: dict) -> Approval:
        for key, value in data.items():
            setattr(approval, key, value)
        await self.db.commit()
        await self.db.refresh(approval)
        stmt = (
            select(Approval)
            .options(selectinload(Approval.approver))
            .where(Approval.id == approval.id)
        )
        return await self.db.scalar(stmt)
