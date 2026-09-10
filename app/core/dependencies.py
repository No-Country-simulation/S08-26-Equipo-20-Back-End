from typing import Annotated, AsyncGenerator

from jose import JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import SessionLocal
from app.core.security import decode_token
from app.modules.auth.repository import AuthRepository
from app.modules.users.model import User

bearer_scheme = HTTPBearer(auto_error=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session


DbDep = Annotated[AsyncSession, Depends(get_db)]


def get_current_user_id(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> str:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    try:
        payload = decode_token(credentials.credentials)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    return payload["sub"]


CurrentUserId = Annotated[str, Depends(get_current_user_id)]


async def get_current_user(
    user_id: CurrentUserId,
    db: DbDep,
) -> User:
    user = await AuthRepository(db).get_user_by_id(int(user_id))
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


class RequireRole:
    def __init__(self, *roles: str):
        self.roles = set(roles)

    async def __call__(self, user: CurrentUser) -> User:
        if user.role.name not in self.roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permisos para realizar esta acción",
            )
        return user


AdminUser = Annotated[User, Depends(RequireRole("ADMIN"))]