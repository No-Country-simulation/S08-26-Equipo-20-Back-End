from fastapi import HTTPException, status

from app.modules.teams.repository import TeamsRepository
from app.modules.teams.schemas import TeamCreate, TeamUpdate


class TeamsService:
    def __init__(self, repository: TeamsRepository):
        self.repository = repository

    async def list_all(self):
        return await self.repository.list_all()

    async def get_by_id(self, team_id: int):
        team = await self.repository.get_by_id(team_id)
        if not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Equipo no encontrado",
            )
        return team

    async def create(self, data: TeamCreate):
        existing = await self.repository.get_by_name(data.name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe un equipo con ese nombre",
            )
        return await self.repository.create(data.model_dump())

    async def update(self, team_id: int, data: TeamUpdate):
        team = await self.repository.get_by_id(team_id)
        if not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Equipo no encontrado",
            )
        updates = data.model_dump(exclude_unset=True)
        if not updates:
            return team
        if "name" in updates:
            existing = await self.repository.get_by_name(updates["name"])
            if existing and existing.id != team_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Ya existe un equipo con ese nombre",
                )
        return await self.repository.update(team, updates)

    async def delete(self, team_id: int):
        team = await self.repository.get_by_id(team_id)
        if not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Equipo no encontrado",
            )
        if await self.repository.has_users(team_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="No se puede eliminar un equipo con usuarios asociados",
            )
        if await self.repository.has_requests(team_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="No se puede eliminar un equipo con solicitudes asociadas",
            )
        await self.repository.delete(team)
