from fastapi import HTTPException, status

from app.core.security import create_access_token, hash_password, verify_password
from app.modules.auth.repository import AuthRepository
from app.modules.users.model import User

INVALID_CREDENTIALS = "Credenciales inválidas"


class AuthService:
    def __init__(self, repository: AuthRepository):
        self.repository = repository

    async def login(self, email: str, password: str) -> tuple[User, str]:
        user = await self.repository.get_user_by_email(email)
        if user is None or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=INVALID_CREDENTIALS,
            )
        if not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=INVALID_CREDENTIALS,
            )
        token = create_access_token(str(user.id))
        return user, token

    async def change_password(
        self, user: User, current_password: str, new_password: str
    ) -> str:
        if not verify_password(current_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Contraseña actual incorrecta",
            )
        new_hash = hash_password(new_password)
        await self.repository.update_password(user, new_hash)
        return create_access_token(str(user.id))