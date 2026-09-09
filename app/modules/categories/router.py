from fastapi import APIRouter

from app.core.dependencies import AdminUser, CurrentUser, DbDep
from app.modules.categories.repository import CategoriesRepository
from app.modules.categories.schemas import CategoryCreate, CategoryOut, CategoryUpdate
from app.modules.categories.service import CategoriesService

router = APIRouter(prefix="/categories", tags=["categories"])


def _service(db) -> CategoriesService:
    return CategoriesService(CategoriesRepository(db))


@router.get("/", response_model=list[CategoryOut])
async def list_categories(user: CurrentUser, db: DbDep):
    return await _service(db).list_all()


@router.post("/", response_model=CategoryOut, status_code=201)
async def create_category(payload: CategoryCreate, user: AdminUser, db: DbDep):
    return await _service(db).create(payload)


@router.patch("/{category_id}", response_model=CategoryOut)
async def update_category(category_id: int, payload: CategoryUpdate, user: AdminUser, db: DbDep):
    return await _service(db).update(category_id, payload)


@router.delete("/{category_id}", status_code=204)
async def delete_category(category_id: int, user: AdminUser, db: DbDep):
    await _service(db).delete(category_id)
