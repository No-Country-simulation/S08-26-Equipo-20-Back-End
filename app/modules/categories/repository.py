from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.categories.model import Categorie
from app.modules.requests.model import Request


class CategoriesRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, category_id: int) -> Categorie | None:
        return await self.db.get(Categorie, category_id)

    async def get_by_name(self, name: str) -> Categorie | None:
        stmt = select(Categorie).where(Categorie.name == name)
        return await self.db.scalar(stmt)

    async def list_all(self) -> list[Categorie]:
        stmt = select(Categorie).order_by(Categorie.name)
        result = await self.db.scalars(stmt)
        return list(result.all())

    async def create(self, data: dict) -> Categorie:
        category = Categorie(**data)
        self.db.add(category)
        await self.db.commit()
        await self.db.refresh(category)
        return category

    async def update(self, category: Categorie, data: dict) -> Categorie:
        for key, value in data.items():
            setattr(category, key, value)
        await self.db.commit()
        await self.db.refresh(category)
        return category

    async def delete(self, category: Categorie) -> None:
        await self.db.delete(category)
        await self.db.commit()

    async def has_requests(self, category_id: int) -> bool:
        stmt = select(exists().where(Request.category_id == category_id))
        return await self.db.scalar(stmt)
