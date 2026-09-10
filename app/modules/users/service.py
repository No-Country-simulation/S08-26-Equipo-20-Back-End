import secrets
import string

from fastapi import HTTPException, status

from app.core.security import hash_password
from app.modules.users.model import User
from app.modules.users.repository import UsersRepository
from app.modules.users.schemas import UserCreate, UserUpdate

TEMPORARY_PASSWORD_LENGTH = 12
USER_NOT_FOUND = "Usuario no encontrado"


def _generate_temporary_password() -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(TEMPORARY_PASSWORD_LENGTH))


class UsersService:
    def __init__(self, repository: UsersRepository):
        self.repository = repository

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
        return await self.repository.list(
            search=search,
            role=role,
            team_id=team_id,
            is_active=is_active,
            offset=offset,
            limit=limit,
        )

    async def get(self, user_id: int) -> User:
        user = await self.repository.get_by_id(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=USER_NOT_FOUND,
            )
        return user

    async def create(self, payload: UserCreate) -> tuple[User, str | None]:
        if await self.repository.get_by_email(payload.email) is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe un usuario con ese email",
            )
        if await self.repository.get_role_by_id(payload.role_id) is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Rol no válido",
            )
        if payload.team_id is not None and not await self.repository.team_exists(
            payload.team_id
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Equipo no válido",
            )

        if payload.password is not None:
            password = payload.password
            temporary_password = None
            must_change_password = False
        else:
            password = _generate_temporary_password()
            temporary_password = password
            must_change_password = True

        user = await self.repository.create(
            User(
                name=payload.name,
                email=payload.email,
                password_hash=hash_password(password),
                role_id=payload.role_id,
                team_id=payload.team_id,
                must_change_password=must_change_password,
            )
        )
        return user, temporary_password

    async def update(self, user_id: int, payload: UserUpdate, actor: User) -> User:
        user = await self.get(user_id)
        fields = payload.model_fields_set

        if "name" in fields:
            user.name = payload.name

        if "role_id" in fields:
            if payload.role_id is not None and await self.repository.get_role_by_id(
                payload.role_id
            ) is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Rol no válido",
                )
            user.role_id = payload.role_id

        if "team_id" in fields:
            if payload.team_id is not None and not await self.repository.team_exists(
                payload.team_id
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Equipo no válido",
                )
            user.team_id = payload.team_id

        if "is_active" in fields:
            await self._validate_deactivation(payload.is_active, user, actor)
            user.is_active = payload.is_active

        await self.repository.commit()
        return await self.get(user_id)

    async def deactivate(self, user_id: int, actor: User) -> User:
        user = await self.get(user_id)
        if not user.is_active:
            return user
        return await self.update(user_id, UserUpdate(is_active=False), actor)

    async def _validate_deactivation(
        self, is_active: bool | None, user: User, actor: User
    ) -> None:
        if is_active is not False or user.role.name != "ADMIN":
            return
        if user.id == actor.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Un administrador no puede desactivarse a sí mismo",
            )
        if await self.repository.count_active_admins() <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede desactivar al último administrador activo",
            )