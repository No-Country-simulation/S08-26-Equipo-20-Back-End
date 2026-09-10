from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.categories.model import Categorie
from app.modules.priorities.model import Prioritie
from app.modules.requests.model import ApprovalStatus, RequestStatus
from app.modules.requests.repository import RequestsRepository
from app.modules.requests.schemas import (
    ApprovalDecision,
    CommentCreate,
    RequestCreate,
    RequestUpdate,
    SlaCreate,
    StatusUpdate,
)
from app.modules.teams.model import Team
from app.modules.users.model import User

# SLA defaults
DEFAULT_RESPONSE_HOURS = 24
DEFAULT_RESOLUTION_HOURS = 72


class RequestsService:
    def __init__(self, repository: RequestsRepository, db: AsyncSession):
        self.repository = repository
        self.db = db

    # --- Helpers ---

    async def _get_request_or_404(self, request_id: int):
        request = await self.repository.get_by_id(request_id)
        if not request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Solicitud no encontrada",
            )
        return request

    # --- CRUD ---

    async def create(self, user: User, data: RequestCreate):
        return await self.repository.create(
            {"description": data.description, "created_by": user.id}
        )

    async def list_requests(self, user: User):
        if user.role.name == "USER":
            return await self.repository.list_by_creator(user.id)
        return await self.repository.list_all()

    async def get(self, request_id: int, user: User):
        request = await self._get_request_or_404(request_id)
        if user.role.name == "USER" and request.created_by != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene acceso a esta solicitud",
            )
        return request

    async def classify(self, request_id: int, user: User, data: RequestUpdate):
        request = await self._get_request_or_404(request_id)
        updates = data.model_dump(exclude_unset=True)
        if not updates:
            return request

        # Validate referenced entities exist
        if "category_id" in updates:
            category = await self.db.get(Categorie, updates["category_id"])
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Categoría no encontrada",
                )

        if "priority_id" in updates:
            priority = await self.db.get(Prioritie, updates["priority_id"])
            if not priority:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Prioridad no encontrada",
                )

        if "team_id" in updates:
            team = await self.db.get(Team, updates["team_id"])
            if not team:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Equipo no encontrado",
                )

        if "assigned_to" in updates:
            assignee = await self.db.get(User, updates["assigned_to"])
            if not assignee:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Usuario asignado no encontrado",
                )

        # Track history for each changed field
        for field, new_val in updates.items():
            old_val = getattr(request, field)
            if old_val != new_val:
                await self.repository.add_history(
                    request_id=request_id,
                    user_id=user.id,
                    action=f"change_{field}",
                    old_value=str(old_val) if old_val is not None else None,
                    new_value=str(new_val),
                )

        # Check if this is the first agent assignment
        is_first_assignment = (
            "assigned_to" in updates
            and request.assigned_to is None
            and updates["assigned_to"] is not None
        )

        # Apply updates
        result = await self.repository.update(request, updates)

        # Auto-create SLA with defaults if not exists
        if is_first_assignment:
            now = datetime.now(timezone.utc)
            sla = await self.repository.get_sla_by_request(request_id)
            if sla:
                await self.repository.update_sla(sla, {"responded_at": now})
            else:
                await self.repository.create_sla(
                    request_id,
                    {
                        "response_deadline": now
                        + timedelta(hours=DEFAULT_RESPONSE_HOURS),
                        "resolution_deadline": now
                        + timedelta(hours=DEFAULT_RESOLUTION_HOURS),
                        "responded_at": now,
                    },
                )

        # Auto-create approval if category requires it
        if "category_id" in updates:
            category = await self.db.get(Categorie, updates["category_id"])
            if category and category.requires_approval:
                await self.repository.create_approval(
                    request_id=request_id,
                    approver_id=user.id,
                )

        return result

    async def change_status(
        self, request_id: int, user: User, data: StatusUpdate
    ):
        request = await self._get_request_or_404(request_id)
        old_status = request.status
        new_status = data.status

        if old_status == new_status:
            return request

        # Track status change in history
        await self.repository.add_history(
            request_id=request_id,
            user_id=user.id,
            action="change_status",
            old_value=old_status.value,
            new_value=new_status.value,
        )

        update_data: dict = {"status": new_status}

        # Set resolved_at when resolving
        if new_status == RequestStatus.RESOLVED:
            now = datetime.now(timezone.utc)
            update_data["resolved_at"] = now
            sla = await self.repository.get_sla_by_request(request_id)
            if sla:
                await self.repository.update_sla(sla, {"resolved_at": now})

        # Set closed_at when closing
        if new_status == RequestStatus.CLOSED:
            update_data["closed_at"] = datetime.now(timezone.utc)

        return await self.repository.update(request, update_data)

    # --- Comments ---

    async def add_comment(
        self, request_id: int, user: User, data: CommentCreate
    ):
        await self._get_request_or_404(request_id)

        # Only AGENT/ADMIN can create internal notes
        if data.is_internal and user.role.name not in ("AGENT", "ADMIN"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo agentes y administradores pueden crear notas internas",
            )

        return await self.repository.add_comment(
            request_id=request_id,
            user_id=user.id,
            content=data.content,
            is_internal=data.is_internal,
        )

    async def list_comments(self, request_id: int, user: User):
        await self._get_request_or_404(request_id)
        include_internal = user.role.name in ("AGENT", "ADMIN")
        return await self.repository.list_comments(
            request_id, include_internal=include_internal
        )

    # --- History ---

    async def list_history(self, request_id: int):
        await self._get_request_or_404(request_id)
        return await self.repository.list_history(request_id)

    # --- SLA ---

    async def get_sla(self, request_id: int):
        await self._get_request_or_404(request_id)
        sla = await self.repository.get_sla_by_request(request_id)
        if not sla:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="SLA no encontrado para esta solicitud",
            )
        return self._enrich_sla(sla)

    async def upsert_sla(self, request_id: int, user: User, data: SlaCreate):
        await self._get_request_or_404(request_id)
        sla = await self.repository.get_sla_by_request(request_id)
        updates = data.model_dump(exclude_unset=True)
        if sla:
            result = await self.repository.update_sla(sla, updates)
        else:
            result = await self.repository.create_sla(request_id, updates)
        return self._enrich_sla(result)

    @staticmethod
    def _enrich_sla(sla):
        """Compute compliance fields for SLA response."""
        response_on_time = None
        resolution_on_time = None
        if sla.response_deadline and sla.responded_at:
            response_on_time = sla.responded_at <= sla.response_deadline
        if sla.resolution_deadline and sla.resolved_at:
            resolution_on_time = sla.resolved_at <= sla.resolution_deadline
        return {
            "id": sla.id,
            "response_deadline": sla.response_deadline,
            "resolution_deadline": sla.resolution_deadline,
            "responded_at": sla.responded_at,
            "resolved_at": sla.resolved_at,
            "response_on_time": response_on_time,
            "resolution_on_time": resolution_on_time,
            "created_at": sla.created_at,
        }

    # --- Approvals ---

    async def list_approvals(self, request_id: int):
        await self._get_request_or_404(request_id)
        return await self.repository.list_approvals(request_id)

    async def decide_approval(
        self,
        request_id: int,
        approval_id: int,
        user: User,
        data: ApprovalDecision,
    ):
        await self._get_request_or_404(request_id)

        approval = await self.repository.get_approval(approval_id)
        if not approval or approval.request_id != request_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Aprobación no encontrada",
            )

        if approval.status != ApprovalStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Esta aprobación ya fue decidida",
            )

        if data.status not in (ApprovalStatus.APPROVED, ApprovalStatus.REJECTED):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El estado debe ser APPROVED o REJECTED",
            )

        return await self.repository.update_approval(
            approval,
            {
                "status": data.status,
                "comment": data.comment,
                "decided_at": datetime.now(timezone.utc),
            },
        )
