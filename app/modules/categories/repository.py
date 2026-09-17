from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.categories.model import Categorie
from app.modules.requests.model import Request


class CategoriesRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list(
        self,
        *,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[Categorie], int]:
        total = await self.db.scalar(select(func.count()).select_from(Categorie))
        result = await self.db.scalars(
            select(Categorie).order_by(Categorie.id).offset(offset).limit(limit)
        )
        return list(result.all()), total or 0

    async def get_by_id(self, category_id: int) -> Categorie | None:
        stmt = (
            select(Categorie)
            .where(Categorie.id == category_id)
            .execution_options(populate_existing=True)
        )
        return await self.db.scalar(stmt)

    async def get_by_name(self, name: str) -> Categorie | None:
        return await self.db.scalar(select(Categorie).where(Categorie.name == name))

    async def has_requests(self, category_id: int) -> bool:
        stmt = (
            select(func.count())
            .select_from(Request)
            .where(Request.category_id == category_id)
        )
        return (await self.db.scalar(stmt)) or 0 > 0

    async def create(self, category: Categorie) -> Categorie:
        self.db.add(category)
        await self.db.commit()
        return await self.get_by_id(category.id)

    async def commit(self) -> None:
        await self.db.commit()

    async def delete(self, category: Categorie) -> None:
        await self.db.delete(category)
        await self.db.commit()