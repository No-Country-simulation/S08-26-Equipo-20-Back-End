from fastapi import HTTPException, status

from app.modules.priorities.repository import PrioritiesRepository
from app.modules.priorities.schemas import PriorityCreate, PriorityUpdate


class PrioritiesService:
    def __init__(self, repository: PrioritiesRepository):
        self.repository = repository

    async def list_all(self):
        return await self.repository.list_all()

    async def create(self, data: PriorityCreate):
        existing_name = await self.repository.get_by_name(data.name)
        if existing_name:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe una prioridad con ese nombre",
            )
        existing_level = await self.repository.get_by_level(data.level)
        if existing_level:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe una prioridad con ese nivel",
            )
        return await self.repository.create(data.model_dump())

    async def update(self, priority_id: int, data: PriorityUpdate):
        priority = await self.repository.get_by_id(priority_id)
        if not priority:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Prioridad no encontrada",
            )
        updates = data.model_dump(exclude_unset=True)
        if not updates:
            return priority
        if "name" in updates:
            existing = await self.repository.get_by_name(updates["name"])
            if existing and existing.id != priority_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Ya existe una prioridad con ese nombre",
                )
        if "level" in updates:
            existing = await self.repository.get_by_level(updates["level"])
            if existing and existing.id != priority_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Ya existe una prioridad con ese nivel",
                )
        return await self.repository.update(priority, updates)

    async def delete(self, priority_id: int):
        priority = await self.repository.get_by_id(priority_id)
        if not priority:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Prioridad no encontrada",
            )
        if await self.repository.has_requests(priority_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="No se puede eliminar una prioridad con solicitudes asociadas",
            )
        await self.repository.delete(priority)
