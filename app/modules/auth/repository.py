from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.users.model import User


class AuthRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_email(self, email: str) -> User | None:
        stmt = (
            select(User)
            .options(selectinload(User.role), selectinload(User.team))
            .where(User.email == email)
        )
        return await self.db.scalar(stmt)

    async def get_user_by_id(self, user_id: int) -> User | None:
        stmt = (
            select(User)
            .options(selectinload(User.role), selectinload(User.team))
            .where(User.id == user_id)
        )
        return await self.db.scalar(stmt)

    async def update_password(self, user: User, password_hash: str) -> None:
        user.password_hash = password_hash
        user.must_change_password = False
        await self.db.commit()