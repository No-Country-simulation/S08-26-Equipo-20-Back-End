from fastapi import HTTPException, status

from app.modules.categories.repository import CategoriesRepository
from app.modules.categories.schemas import CategoryCreate, CategoryUpdate


class CategoriesService:
    def __init__(self, repository: CategoriesRepository):
        self.repository = repository

    async def list_all(self):
        return await self.repository.list_all()

    async def create(self, data: CategoryCreate):
        existing = await self.repository.get_by_name(data.name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe una categoría con ese nombre",
            )
        return await self.repository.create(data.model_dump())

    async def update(self, category_id: int, data: CategoryUpdate):
        category = await self.repository.get_by_id(category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoría no encontrada",
            )
        updates = data.model_dump(exclude_unset=True)
        if not updates:
            return category
        if "name" in updates:
            existing = await self.repository.get_by_name(updates["name"])
            if existing and existing.id != category_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Ya existe una categoría con ese nombre",
                )
        return await self.repository.update(category, updates)

    async def delete(self, category_id: int):
        category = await self.repository.get_by_id(category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoría no encontrada",
            )
        if await self.repository.has_requests(category_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="No se puede eliminar una categoría con solicitudes asociadas",
            )
        await self.repository.delete(category)
