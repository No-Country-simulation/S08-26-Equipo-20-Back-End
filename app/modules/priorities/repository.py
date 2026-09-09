from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.priorities.model import Prioritie
from app.modules.requests.model import Request


class PrioritiesRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, priority_id: int) -> Prioritie | None:
        return await self.db.get(Prioritie, priority_id)

    async def get_by_name(self, name: str) -> Prioritie | None:
        stmt = select(Prioritie).where(Prioritie.name == name)
        return await self.db.scalar(stmt)

    async def get_by_level(self, level: int) -> Prioritie | None:
        stmt = select(Prioritie).where(Prioritie.level == level)
        return await self.db.scalar(stmt)

    async def list_all(self) -> list[Prioritie]:
        stmt = select(Prioritie).order_by(Prioritie.level)
        result = await self.db.scalars(stmt)
        return list(result.all())

    async def create(self, data: dict) -> Prioritie:
        priority = Prioritie(**data)
        self.db.add(priority)
        await self.db.commit()
        await self.db.refresh(priority)
        return priority

    async def update(self, priority: Prioritie, data: dict) -> Prioritie:
        for key, value in data.items():
            setattr(priority, key, value)
        await self.db.commit()
        await self.db.refresh(priority)
        return priority

    async def delete(self, priority: Prioritie) -> None:
        await self.db.delete(priority)
        await self.db.commit()

    async def has_requests(self, priority_id: int) -> bool:
        stmt = select(exists().where(Request.priority_id == priority_id))
        return await self.db.scalar(stmt)
