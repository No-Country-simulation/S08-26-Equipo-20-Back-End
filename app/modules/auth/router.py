from fastapi import APIRouter

from app.core.dependencies import CurrentUser, DbDep
from app.modules.auth.repository import AuthRepository
from app.modules.auth.schemas import (
    ChangePasswordRequest,
    LoginRequest,
    TokenResponse,
    UserResponse,
)
from app.modules.auth.service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: DbDep) -> TokenResponse:
    service = AuthService(AuthRepository(db))
    _, token = await service.login(payload.email, payload.password)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse)
async def me(user: CurrentUser) -> UserResponse:
    return user


@router.post("/change-password", response_model=TokenResponse)
async def change_password(
    payload: ChangePasswordRequest,
    user: CurrentUser,
    db: DbDep,
) -> TokenResponse:
    service = AuthService(AuthRepository(db))
    token = await service.change_password(
        user, payload.current_password, payload.new_password
    )
    return TokenResponse(access_token=token)