from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.teams.model import Team
from app.modules.users.model import Role, User


class UsersRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    def _base_stmt(self):
        return select(User).options(selectinload(User.role), selectinload(User.team))

    async def list(
        self,
        *,
        search: str | None = None,
        role: str | None = None,
        team_id: int | None = None,
        is_active: bool | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[User], int]:
        filters = []
        if search:
            pattern = f"%{search}%"
            filters.append(or_(User.name.ilike(pattern), User.email.ilike(pattern)))
        if role:
            filters.append(User.role.has(Role.name == role))
        if team_id is not None:
            filters.append(User.team_id == team_id)
        if is_active is not None:
            filters.append(User.is_active == is_active)

        total = await self.db.scalar(
            select(func.count()).select_from(User).where(*filters)
        )
        result = await self.db.scalars(
            self._base_stmt()
            .where(*filters)
            .order_by(User.id)
            .offset(offset)
            .limit(limit)
        )
        return list(result.all()), total or 0

    async def get_by_id(self, user_id: int) -> User | None:
        return await self.db.scalar(self._base_stmt().where(User.id == user_id))

    async def get_by_email(self, email: str) -> User | None:
        return await self.db.scalar(self._base_stmt().where(User.email == email))

    async def get_role_by_id(self, role_id: int) -> Role | None:
        return await self.db.get(Role, role_id)

    async def team_exists(self, team_id: int) -> bool:
        return await self.db.get(Team, team_id) is not None

    async def count_active_admins(self) -> int:
        stmt = (
            select(func.count())
            .select_from(User)
            .join(User.role)
            .where(User.is_active.is_(True), Role.name == "ADMIN")
        )
        return (await self.db.scalar(stmt)) or 0

    async def create(self, user: User) -> User:
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def commit(self) -> None:
        await self.db.commit()