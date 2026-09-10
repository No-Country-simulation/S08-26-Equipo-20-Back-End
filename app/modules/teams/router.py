from fastapi import APIRouter, Query, status

from app.core.dependencies import AdminUser, CurrentUser, DbDep
from app.modules.teams.repository import TeamsRepository
from app.modules.teams.schemas import (
    TeamCreate,
    TeamList,
    TeamResponse,
    TeamUpdate,
)
from app.modules.teams.service import TeamsService

router = APIRouter(prefix="/teams", tags=["teams"])


@router.get("", response_model=TeamList)
async def list_teams(
    _: CurrentUser,
    db: DbDep,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
) -> TeamList:
    service = TeamsService(TeamsRepository(db))
    items, total = await service.list(offset=offset, limit=limit)
    return TeamList(items=items, total=total)


@router.post("", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
async def create_team(payload: TeamCreate, _: AdminUser, db: DbDep) -> TeamResponse:
    service = TeamsService(TeamsRepository(db))
    return await service.create(payload)


@router.get("/{team_id}", response_model=TeamResponse)
async def get_team(team_id: int, _: CurrentUser, db: DbDep) -> TeamResponse:
    service = TeamsService(TeamsRepository(db))
    return await service.get(team_id)


@router.patch("/{team_id}", response_model=TeamResponse)
async def update_team(
    team_id: int,
    payload: TeamUpdate,
    _: AdminUser,
    db: DbDep,
) -> TeamResponse:
    service = TeamsService(TeamsRepository(db))
    return await service.update(team_id, payload)


@router.delete(
    "/{team_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_team(team_id: int, _: AdminUser, db: DbDep) -> None:
    service = TeamsService(TeamsRepository(db))
    await service.delete(team_id)