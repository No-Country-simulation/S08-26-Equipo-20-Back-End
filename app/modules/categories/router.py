from fastapi import APIRouter, Query, status

from app.core.dependencies import AdminUser, CurrentUser, DbDep
from app.modules.categories.repository import CategoriesRepository
from app.modules.categories.schemas import (
    CategoryCreate,
    CategoryList,
    CategoryResponse,
    CategoryUpdate,
)
from app.modules.categories.service import CategoriesService

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=CategoryList)
async def list_categories(
    _: CurrentUser,
    db: DbDep,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
) -> CategoryList:
    service = CategoriesService(CategoriesRepository(db))
    items, total = await service.list(offset=offset, limit=limit)
    return CategoryList(items=items, total=total)


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    payload: CategoryCreate, _: AdminUser, db: DbDep
) -> CategoryResponse:
    service = CategoriesService(CategoriesRepository(db))
    return await service.create(payload)


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: int, _: CurrentUser, db: DbDep
) -> CategoryResponse:
    service = CategoriesService(CategoriesRepository(db))
    return await service.get(category_id)


@router.patch("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    payload: CategoryUpdate,
    _: AdminUser,
    db: DbDep,
) -> CategoryResponse:
    service = CategoriesService(CategoriesRepository(db))
    return await service.update(category_id, payload)


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_category(category_id: int, _: AdminUser, db: DbDep) -> None:
    service = CategoriesService(CategoriesRepository(db))
    await service.delete(category_id)