from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.teams.model import Team
from app.modules.requests.model import Request
from app.modules.users.model import User


class TeamsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, team_id: int) -> Team | None:
        return await self.db.get(Team, team_id)

    async def get_by_name(self, name: str) -> Team | None:
        stmt = select(Team).where(Team.name == name)
        return await self.db.scalar(stmt)

    async def list_all(self) -> list[Team]:
        stmt = select(Team).order_by(Team.name)
        result = await self.db.scalars(stmt)
        return list(result.all())

    async def create(self, data: dict) -> Team:
        team = Team(**data)
        self.db.add(team)
        await self.db.commit()
        await self.db.refresh(team)
        return team

    async def update(self, team: Team, data: dict) -> Team:
        for key, value in data.items():
            setattr(team, key, value)
        await self.db.commit()
        await self.db.refresh(team)
        return team

    async def delete(self, team: Team) -> None:
        await self.db.delete(team)
        await self.db.commit()

    async def has_users(self, team_id: int) -> bool:
        stmt = select(exists().where(User.team_id == team_id))
        return await self.db.scalar(stmt)

    async def has_requests(self, team_id: int) -> bool:
        stmt = select(exists().where(Request.team_id == team_id))
        return await self.db.scalar(stmt)
