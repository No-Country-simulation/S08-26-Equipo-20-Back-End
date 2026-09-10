from typing import Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.requests.model import Attachment, Comment, Request
from app.modules.users.model import User

from .schemas import CommentCreate, CustomerRequestCreate


class SQLCustomerRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_request_by_id(self, request_id: int) -> dict[str, Any] | None:
        stmt = select(Request).where(Request.id == request_id)
        result = await self.db.execute(stmt)
        req = result.scalar_one_or_none()
        if not req:
            return None
        return {
            "id": req.id,
            "description": req.description,
            "status": req.status,
            "created_by": req.created_by,
        }

    async def create_request(self, user_id: int, request_in: CustomerRequestCreate) -> dict[str, Any]:
        new_req = Request(
            description=request_in.description,
            created_by=user_id,
            status="NEW",
        )
        self.db.add(new_req)
        await self.db.commit()
        await self.db.refresh(new_req)
        return {
            "id": new_req.id,
            "description": new_req.description,
            "status": new_req.status,
            "category_id": new_req.category_id,
            "priority_id": new_req.priority_id,
            "team_id": new_req.team_id,
            "created_by": new_req.created_by,
            "assigned_to": new_req.assigned_to,
            "created_at": new_req.created_at,
            "updated_at": new_req.updated_at,
            "resolved_at": new_req.resolved_at,
            "closed_at": new_req.closed_at,
        }

    async def list_requests_by_user(
        self, user_id: int, offset: int = 0, limit: int = 20
    ) -> list[dict[str, Any]]:
        stmt = (
            select(Request)
            .where(Request.created_by == user_id)
            .order_by(Request.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        requests = result.scalars().all()

        return [
            {
                "id": r.id,
                "description": r.description,
                "status": r.status,
                "category_id": r.category_id,
                "priority_id": r.priority_id,
                "team_id": r.team_id,
                "created_by": r.created_by,
                "assigned_to": r.assigned_to,
                "created_at": r.created_at,
                "updated_at": r.updated_at,
                "resolved_at": r.resolved_at,
                "closed_at": r.closed_at,
            }
            for r in requests
        ]

    async def get_request_detail(self, request_id: int) -> dict[str, Any] | None:
        stmt = (
            select(Request)
            .options(
                selectinload(Request.category),
                selectinload(Request.priority),
                selectinload(Request.team),
                selectinload(Request.creator),
                selectinload(Request.assignee),
                selectinload(Request.comments).selectinload(Comment.user),
                selectinload(Request.attachments),
            )
            .where(Request.id == request_id)
        )
        result = await self.db.execute(stmt)
        req = result.scalar_one_or_none()
        if not req:
            return None

        public_comments = [c for c in req.comments if not c.is_internal]

        return {
            "id": req.id,
            "description": req.description,
            "status": req.status,
            "category_id": req.category_id,
            "priority_id": req.priority_id,
            "team_id": req.team_id,
            "created_by": req.created_by,
            "assigned_to": req.assigned_to,
            "created_at": req.created_at,
            "updated_at": req.updated_at,
            "resolved_at": req.resolved_at,
            "closed_at": req.closed_at,
            "category": (
                {"id": req.category.id, "name": req.category.name, "description": req.category.description}
                if req.category else None
            ),
            "priority": (
                {"id": req.priority.id, "name": req.priority.name, "level": req.priority.level}
                if req.priority else None
            ),
            "team": (
                {"id": req.team.id, "name": req.team.name, "description": req.team.description}
                if req.team else None
            ),
            "creator": (
                {"id": req.creator.id, "name": req.creator.name, "email": req.creator.email}
                if req.creator else None
            ),
            "assignee": (
                {"id": req.assignee.id, "name": req.assignee.name, "email": req.assignee.email}
                if req.assignee else None
            ),
            "comments": [
                {
                    "id": c.id,
                    "request_id": c.request_id,
                    "user_id": c.user_id,
                    "content": c.content,
                    "is_internal": c.is_internal,
                    "created_at": c.created_at,
                    "user": (
                        {"id": c.user.id, "name": c.user.name, "email": c.user.email}
                        if c.user else None
                    ),
                }
                for c in sorted(public_comments, key=lambda x: x.created_at)
            ],
            "attachments": [
                {
                    "id": a.id,
                    "request_id": a.request_id,
                    "uploaded_by": a.uploaded_by,
                    "file_name": a.file_name,
                    "file_path": a.file_path,
                    "created_at": a.created_at,
                }
                for a in sorted(req.attachments, key=lambda x: x.created_at)
            ],
        }

    async def get_request_status(self, request_id: int) -> str | None:
        stmt = select(Request.status).where(Request.id == request_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_request_priority(self, request_id: int) -> dict[str, Any] | None:
        stmt = (
            select(Request)
            .options(selectinload(Request.priority))
            .where(Request.id == request_id)
        )
        result = await self.db.execute(stmt)
        req = result.scalar_one_or_none()
        if not req or not req.priority:
            return None
        return {
            "id": req.priority.id,
            "name": req.priority.name,
            "level": req.priority.level,
        }

    async def get_request_assignment(self, request_id: int) -> dict[str, Any] | None:
        stmt = (
            select(Request)
            .options(selectinload(Request.team), selectinload(Request.assignee))
            .where(Request.id == request_id)
        )
        result = await self.db.execute(stmt)
        req = result.scalar_one_or_none()
        if not req:
            return None
        return {
            "team": (
                {"id": req.team.id, "name": req.team.name, "description": req.team.description}
                if req.team else None
            ),
            "assignee": (
                {"id": req.assignee.id, "name": req.assignee.name, "email": req.assignee.email}
                if req.assignee else None
            ),
        }

    async def add_comment(
        self, request_id: int, user_id: int, comment_in: CommentCreate
    ) -> dict[str, Any]:
        comment = Comment(
            request_id=request_id,
            user_id=user_id,
            content=comment_in.content,
            is_internal=False,
        )
        self.db.add(comment)
        await self.db.commit()
        await self.db.refresh(comment)

        user_stmt = select(User).where(User.id == user_id)
        user_res = await self.db.execute(user_stmt)
        user = user_res.scalar_one_or_none()

        return {
            "id": comment.id,
            "request_id": comment.request_id,
            "user_id": comment.user_id,
            "content": comment.content,
            "is_internal": comment.is_internal,
            "created_at": comment.created_at,
            "user": (
                {"id": user.id, "name": user.name, "email": user.email}
                if user else None
            ),
        }

    async def add_attachment(
        self, request_id: int, uploaded_by: int, file_name: str, file_path: str
    ) -> dict[str, Any]:
        attachment = Attachment(
            request_id=request_id,
            uploaded_by=uploaded_by,
            file_name=file_name,
            file_path=file_path,
        )
        self.db.add(attachment)
        await self.db.commit()
        await self.db.refresh(attachment)
        return {
            "id": attachment.id,
            "request_id": attachment.request_id,
            "uploaded_by": attachment.uploaded_by,
            "file_name": attachment.file_name,
            "file_path": attachment.file_path,
            "created_at": attachment.created_at,
        }
