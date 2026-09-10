from fastapi import APIRouter, Query, status

from app.core.dependencies import AdminUser, CurrentUser, DbDep
from app.modules.priorities.repository import PrioritiesRepository
from app.modules.priorities.schemas import (
    PriorityCreate,
    PriorityList,
    PriorityResponse,
    PriorityUpdate,
)
from app.modules.priorities.service import PrioritiesService

router = APIRouter(prefix="/priorities", tags=["priorities"])


@router.get("", response_model=PriorityList)
async def list_priorities(
    _: CurrentUser,
    db: DbDep,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
) -> PriorityList:
    service = PrioritiesService(PrioritiesRepository(db))
    items, total = await service.list(offset=offset, limit=limit)
    return PriorityList(items=items, total=total)


@router.post("", response_model=PriorityResponse, status_code=status.HTTP_201_CREATED)
async def create_priority(
    payload: PriorityCreate, _: AdminUser, db: DbDep
) -> PriorityResponse:
    service = PrioritiesService(PrioritiesRepository(db))
    return await service.create(payload)


@router.get("/{priority_id}", response_model=PriorityResponse)
async def get_priority(
    priority_id: int, _: CurrentUser, db: DbDep
) -> PriorityResponse:
    service = PrioritiesService(PrioritiesRepository(db))
    return await service.get(priority_id)


@router.patch("/{priority_id}", response_model=PriorityResponse)
async def update_priority(
    priority_id: int,
    payload: PriorityUpdate,
    _: AdminUser,
    db: DbDep,
) -> PriorityResponse:
    service = PrioritiesService(PrioritiesRepository(db))
    return await service.update(priority_id, payload)


@router.delete(
    "/{priority_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_priority(priority_id: int, _: AdminUser, db: DbDep) -> None:
    service = PrioritiesService(PrioritiesRepository(db))
    await service.delete(priority_id)