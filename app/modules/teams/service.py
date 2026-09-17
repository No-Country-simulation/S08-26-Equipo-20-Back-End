from fastapi import HTTPException, status

from app.modules.teams.model import Team
from app.modules.teams.repository import TeamsRepository
from app.modules.teams.schemas import TeamCreate, TeamUpdate

TEAM_NOT_FOUND = "Equipo no encontrado"
TEAM_NAME_EXISTS = "Ya existe un equipo con ese nombre"
TEAM_IN_USE = "No se puede eliminar un equipo con usuarios o solicitudes asociadas"


class TeamsService:
    def __init__(self, repository: TeamsRepository):
        self.repository = repository

    async def list(
        self,
        *,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[Team], int]:
        return await self.repository.list(offset=offset, limit=limit)

    async def get(self, team_id: int) -> Team:
        team = await self.repository.get_by_id(team_id)
        if team is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=TEAM_NOT_FOUND,
            )
        return team

    async def create(self, payload: TeamCreate) -> Team:
        if await self.repository.get_by_name(payload.name) is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=TEAM_NAME_EXISTS,
            )
        return await self.repository.create(
            Team(name=payload.name, description=payload.description)
        )

    async def update(self, team_id: int, payload: TeamUpdate) -> Team:
        team = await self.get(team_id)
        fields = payload.model_fields_set

        if "name" in fields:
            if payload.name is not None and await self.repository.get_by_name(
                payload.name
            ) is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=TEAM_NAME_EXISTS,
                )
            team.name = payload.name

        if "description" in fields:
            team.description = payload.description

        await self.repository.commit()
        return await self.get(team_id)

    async def delete(self, team_id: int) -> None:
        team = await self.get(team_id)
        if await self.repository.has_users(team_id) or await self.repository.has_requests(
            team_id
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=TEAM_IN_USE,
            )
        await self.repository.delete(team)