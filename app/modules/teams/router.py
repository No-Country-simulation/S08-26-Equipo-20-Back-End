from fastapi import APIRouter

from app.core.dependencies import AdminUser, CurrentUser, DbDep
from app.modules.teams.repository import TeamsRepository
from app.modules.teams.schemas import TeamCreate, TeamOut, TeamUpdate
from app.modules.teams.service import TeamsService

router = APIRouter(prefix="/teams", tags=["teams"])


def _service(db) -> TeamsService:
    return TeamsService(TeamsRepository(db))


@router.get("/", response_model=list[TeamOut])
async def list_teams(user: CurrentUser, db: DbDep):
    return await _service(db).list_all()


@router.post("/", response_model=TeamOut, status_code=201)
async def create_team(payload: TeamCreate, user: AdminUser, db: DbDep):
    return await _service(db).create(payload)


@router.get("/{team_id}", response_model=TeamOut)
async def get_team(team_id: int, user: AdminUser, db: DbDep):
    return await _service(db).get_by_id(team_id)


@router.patch("/{team_id}", response_model=TeamOut)
async def update_team(team_id: int, payload: TeamUpdate, user: AdminUser, db: DbDep):
    return await _service(db).update(team_id, payload)


@router.delete("/{team_id}", status_code=204)
async def delete_team(team_id: int, user: AdminUser, db: DbDep):
    await _service(db).delete(team_id)
