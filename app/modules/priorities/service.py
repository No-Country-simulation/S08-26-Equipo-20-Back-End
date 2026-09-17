from fastapi import HTTPException, status

from app.modules.priorities.model import Prioritie
from app.modules.priorities.repository import PrioritiesRepository
from app.modules.priorities.schemas import PriorityCreate, PriorityUpdate

PRIORITY_NOT_FOUND = "Prioridad no encontrada"
PRIORITY_NAME_EXISTS = "Ya existe una prioridad con ese nombre"
PRIORITY_LEVEL_EXISTS = "Ya existe una prioridad con ese nivel"
PRIORITY_IN_USE = (
    "No se puede eliminar una prioridad con solicitudes asociadas"
)


class PrioritiesService:
    def __init__(self, repository: PrioritiesRepository):
        self.repository = repository

    async def list(
        self,
        *,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[Prioritie], int]:
        return await self.repository.list(offset=offset, limit=limit)

    async def get(self, priority_id: int) -> Prioritie:
        priority = await self.repository.get_by_id(priority_id)
        if priority is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=PRIORITY_NOT_FOUND,
            )
        return priority

    async def create(self, payload: PriorityCreate) -> Prioritie:
        if await self.repository.get_by_name(payload.name) is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=PRIORITY_NAME_EXISTS,
            )
        if await self.repository.get_by_level(payload.level) is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=PRIORITY_LEVEL_EXISTS,
            )
        return await self.repository.create(
            Prioritie(name=payload.name, level=payload.level)
        )

    async def update(
        self, priority_id: int, payload: PriorityUpdate
    ) -> Prioritie:
        priority = await self.get(priority_id)
        fields = payload.model_fields_set

        if "name" in fields:
            if payload.name is not None and await self.repository.get_by_name(
                payload.name
            ) is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=PRIORITY_NAME_EXISTS,
                )
            priority.name = payload.name

        if "level" in fields:
            existing = await self.repository.get_by_level(payload.level)
            if payload.level is not None and existing is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=PRIORITY_LEVEL_EXISTS,
                )
            priority.level = payload.level

        await self.repository.commit()
        return await self.get(priority_id)

    async def delete(self, priority_id: int) -> None:
        priority = await self.get(priority_id)
        if await self.repository.has_requests(priority_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=PRIORITY_IN_USE,
            )
        await self.repository.delete(priority)