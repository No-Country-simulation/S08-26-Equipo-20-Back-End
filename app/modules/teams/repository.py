from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.requests.model import Request
from app.modules.teams.model import Team
from app.modules.users.model import User


class TeamsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list(
        self,
        *,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[Team], int]:
        total = await self.db.scalar(select(func.count()).select_from(Team))
        result = await self.db.scalars(
            select(Team).order_by(Team.id).offset(offset).limit(limit)
        )
        return list(result.all()), total or 0

    async def get_by_id(self, team_id: int) -> Team | None:
        stmt = (
            select(Team)
            .where(Team.id == team_id)
            .execution_options(populate_existing=True)
        )
        return await self.db.scalar(stmt)

    async def get_by_name(self, name: str) -> Team | None:
        return await self.db.scalar(select(Team).where(Team.name == name))

    async def has_users(self, team_id: int) -> bool:
        stmt = select(func.count()).select_from(User).where(User.team_id == team_id)
        return (await self.db.scalar(stmt)) or 0 > 0

    async def has_requests(self, team_id: int) -> bool:
        stmt = select(func.count()).select_from(Request).where(Request.team_id == team_id)
        return (await self.db.scalar(stmt)) or 0 > 0

    async def create(self, team: Team) -> Team:
        self.db.add(team)
        await self.db.commit()
        return await self.get_by_id(team.id)

    async def commit(self) -> None:
        await self.db.commit()

    async def delete(self, team: Team) -> None:
        await self.db.delete(team)
        await self.db.commit()