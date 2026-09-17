from fastapi import APIRouter, Query, status

from app.core.dependencies import AdminUser, CurrentUser, DbDep
from app.modules.users.repository import UsersRepository
from app.modules.users.schemas import (
    UserCreate,
    UserCreateResponse,
    UserList,
    UserResponse,
    UserUpdate,
)
from app.modules.users.service import UsersService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=UserList)
async def list_users(
    _: CurrentUser,
    db: DbDep,
    search: str | None = Query(default=None),
    role: str | None = Query(default=None),
    team_id: int | None = Query(default=None),
    is_active: bool | None = Query(default=None),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
) -> UserList:
    service = UsersService(UsersRepository(db))
    items, total = await service.list(
        search=search,
        role=role,
        team_id=team_id,
        is_active=is_active,
        offset=offset,
        limit=limit,
    )
    return UserList(items=items, total=total)


@router.post("", response_model=UserCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreate,
    _: AdminUser,
    db: DbDep,
) -> UserCreateResponse:
    service = UsersService(UsersRepository(db))
    user, temporary_password = await service.create(payload)
    return UserCreateResponse(
        user=UserResponse.model_validate(user),
        temporary_password=temporary_password,
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, _: CurrentUser, db: DbDep) -> UserResponse:
    service = UsersService(UsersRepository(db))
    return await service.get(user_id)


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    payload: UserUpdate,
    actor: AdminUser,
    db: DbDep,
) -> UserResponse:
    service = UsersService(UsersRepository(db))
    return await service.update(user_id, payload, actor)


@router.delete("/{user_id}", response_model=UserResponse)
async def delete_user(user_id: int, actor: AdminUser, db: DbDep) -> UserResponse:
    service = UsersService(UsersRepository(db))
    return await service.deactivate(user_id, actor)