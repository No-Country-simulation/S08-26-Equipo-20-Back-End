from fastapi import APIRouter

from app.core.dependencies import AdminUser, CurrentUser, DbDep
from app.modules.priorities.repository import PrioritiesRepository
from app.modules.priorities.schemas import PriorityCreate, PriorityOut, PriorityUpdate
from app.modules.priorities.service import PrioritiesService

router = APIRouter(prefix="/priorities", tags=["priorities"])


def _service(db) -> PrioritiesService:
    return PrioritiesService(PrioritiesRepository(db))


@router.get("/", response_model=list[PriorityOut])
async def list_priorities(user: CurrentUser, db: DbDep):
    return await _service(db).list_all()


@router.post("/", response_model=PriorityOut, status_code=201)
async def create_priority(payload: PriorityCreate, user: AdminUser, db: DbDep):
    return await _service(db).create(payload)


@router.patch("/{priority_id}", response_model=PriorityOut)
async def update_priority(priority_id: int, payload: PriorityUpdate, user: AdminUser, db: DbDep):
    return await _service(db).update(priority_id, payload)


@router.delete("/{priority_id}", status_code=204)
async def delete_priority(priority_id: int, user: AdminUser, db: DbDep):
    await _service(db).delete(priority_id)
