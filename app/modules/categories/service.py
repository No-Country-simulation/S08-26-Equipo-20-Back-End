from fastapi import HTTPException, status

from app.modules.categories.model import Categorie
from app.modules.categories.repository import CategoriesRepository
from app.modules.categories.schemas import CategoryCreate, CategoryUpdate

CATEGORY_NOT_FOUND = "Categoría no encontrada"
CATEGORY_NAME_EXISTS = "Ya existe una categoría con ese nombre"
CATEGORY_IN_USE = (
    "No se puede eliminar una categoría con solicitudes asociadas"
)


class CategoriesService:
    def __init__(self, repository: CategoriesRepository):
        self.repository = repository

    async def list(
        self,
        *,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[Categorie], int]:
        return await self.repository.list(offset=offset, limit=limit)

    async def get(self, category_id: int) -> Categorie:
        category = await self.repository.get_by_id(category_id)
        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=CATEGORY_NOT_FOUND,
            )
        return category

    async def create(self, payload: CategoryCreate) -> Categorie:
        if await self.repository.get_by_name(payload.name) is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=CATEGORY_NAME_EXISTS,
            )
        return await self.repository.create(
            Categorie(
                name=payload.name,
                description=payload.description,
                requires_approval=payload.requires_approval,
            )
        )

    async def update(
        self, category_id: int, payload: CategoryUpdate
    ) -> Categorie:
        category = await self.get(category_id)
        fields = payload.model_fields_set

        if "name" in fields:
            if payload.name is not None and await self.repository.get_by_name(
                payload.name
            ) is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=CATEGORY_NAME_EXISTS,
                )
            category.name = payload.name

        if "description" in fields:
            category.description = payload.description

        if "requires_approval" in fields:
            category.requires_approval = payload.requires_approval

        await self.repository.commit()
        return await self.get(category_id)

    async def delete(self, category_id: int) -> None:
        category = await self.get(category_id)
        if await self.repository.has_requests(category_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=CATEGORY_IN_USE,
            )
        await self.repository.delete(category)