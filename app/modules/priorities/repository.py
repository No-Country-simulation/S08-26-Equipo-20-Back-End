from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.priorities.model import Prioritie
from app.modules.requests.model import Request


class PrioritiesRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list(
        self,
        *,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[Prioritie], int]:
        total = await self.db.scalar(select(func.count()).select_from(Prioritie))
        result = await self.db.scalars(
            select(Prioritie).order_by(Prioritie.level, Prioritie.id).offset(offset).limit(limit)
        )
        return list(result.all()), total or 0

    async def get_by_id(self, priority_id: int) -> Prioritie | None:
        stmt = (
            select(Prioritie)
            .where(Prioritie.id == priority_id)
            .execution_options(populate_existing=True)
        )
        return await self.db.scalar(stmt)

    async def get_by_name(self, name: str) -> Prioritie | None:
        return await self.db.scalar(select(Prioritie).where(Prioritie.name == name))

    async def get_by_level(self, level: int) -> Prioritie | None:
        stmt = select(Prioritie).where(Prioritie.level == level)
        return await self.db.scalar(stmt)

    async def has_requests(self, priority_id: int) -> bool:
        stmt = (
            select(func.count())
            .select_from(Request)
            .where(Request.priority_id == priority_id)
        )
        return (await self.db.scalar(stmt)) or 0 > 0

    async def create(self, priority: Prioritie) -> Prioritie:
        self.db.add(priority)
        await self.db.commit()
        return await self.get_by_id(priority.id)

    async def commit(self) -> None:
        await self.db.commit()

    async def delete(self, priority: Prioritie) -> None:
        await self.db.delete(priority)
        await self.db.commit()