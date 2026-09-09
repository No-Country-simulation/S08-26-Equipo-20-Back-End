import uuid
from datetime import datetime, timedelta, timezone

import pytest
from httpx import ASGITransport, AsyncClient
from jose import jwt
from sqlalchemy import delete, select

from app.core.config import settings
from app.core.database import SessionLocal
from app.core.security import hash_password
from app.main import app
from app.modules.users.model import Role, User

PASSWORD = "secret123"
INVALID_CREDENTIALS = "Credenciales inválidas"


def unique_email() -> str:
    return f"user-{uuid.uuid4().hex[:8]}@test.com"


async def create_user(
    *,
    email: str,
    password: str = PASSWORD,
    role_name: str = "USER",
    active: bool = True,
    must_change_password: bool = False,
) -> User:
    async with SessionLocal() as session:
        role = await session.scalar(select(Role).where(Role.name == role_name))
        user = User(
            name="Test User",
            email=email,
            password_hash=hash_password(password),
            role_id=role.id,
            is_active=active,
            must_change_password=must_change_password,
        )
        session.add(user)
        await session.commit()
        return user


async def delete_user(email: str) -> None:
    async with SessionLocal() as session:
        await session.execute(delete(User).where(User.email == email))
        await session.commit()


async def login(client: AsyncClient, email: str, password: str) -> str:
    response = await client.post(
        "/auth/login", json={"email": email, "password": password}
    )
    assert response.status_code == 200
    return response.json()["access_token"]


async def auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_login_successful(client):
    email = unique_email()
    await create_user(email=email)
    try:
        response = await client.post(
            "/auth/login", json={"email": email, "password": PASSWORD}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["token_type"] == "bearer"
        assert data["access_token"]
    finally:
        await delete_user(email)


@pytest.mark.asyncio
async def test_login_invalid_password(client):
    email = unique_email()
    await create_user(email=email)
    try:
        response = await client.post(
            "/auth/login", json={"email": email, "password": "wrong-pass"}
        )
        assert response.status_code == 401
        assert response.json()["detail"] == INVALID_CREDENTIALS
    finally:
        await delete_user(email)


@pytest.mark.asyncio
async def test_login_unknown_user(client):
    response = await client.post(
        "/auth/login",
        json={"email": unique_email(), "password": PASSWORD},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == INVALID_CREDENTIALS


@pytest.mark.asyncio
async def test_login_inactive_user(client):
    email = unique_email()
    await create_user(email=email, active=False)
    try:
        response = await client.post(
            "/auth/login", json={"email": email, "password": PASSWORD}
        )
        assert response.status_code == 401
        assert response.json()["detail"] == INVALID_CREDENTIALS
    finally:
        await delete_user(email)


@pytest.mark.asyncio
async def test_me_with_valid_token(client):
    email = unique_email()
    user = await create_user(email=email)
    try:
        token = await login(client, email, PASSWORD)
        response = await client.get("/auth/me", headers=await auth_header(token))
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user.id
        assert data["email"] == email
        assert data["role"] == "USER"
        assert data["must_change_password"] is False
    finally:
        await delete_user(email)


@pytest.mark.asyncio
async def test_me_invalid_token(client):
    response = await client.get(
        "/auth/me", headers=await auth_header("invalid.token.value")
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_expired_token(client):
    token = jwt.encode(
        {"sub": "1", "exp": datetime.now(timezone.utc) - timedelta(minutes=1)},
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )
    response = await client.get("/auth/me", headers=await auth_header(token))
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_without_token(client):
    response = await client.get("/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_change_password_success(client):
    email = unique_email()
    await create_user(email=email)
    try:
        token = await login(client, email, PASSWORD)
        response = await client.post(
            "/auth/change-password",
            headers=await auth_header(token),
            json={"current_password": PASSWORD, "new_password": "newsecret123"},
        )
        assert response.status_code == 200
        assert response.json()["access_token"]

        login_new = await client.post(
            "/auth/login", json={"email": email, "password": "newsecret123"}
        )
        assert login_new.status_code == 200
    finally:
        await delete_user(email)


@pytest.mark.asyncio
async def test_change_password_flag_cleared(client):
    email = unique_email()
    await create_user(email=email, must_change_password=True)
    try:
        token = await login(client, email, PASSWORD)
        await client.post(
            "/auth/change-password",
            headers=await auth_header(token),
            json={"current_password": PASSWORD, "new_password": "newsecret123"},
        )

        new_token = await login(client, email, "newsecret123")
        me = await client.get("/auth/me", headers=await auth_header(new_token))
        assert me.status_code == 200
        assert me.json()["must_change_password"] is False
    finally:
        await delete_user(email)


@pytest.mark.asyncio
async def test_change_password_wrong_current(client):
    email = unique_email()
    await create_user(email=email)
    try:
        token = await login(client, email, PASSWORD)
        response = await client.post(
            "/auth/change-password",
            headers=await auth_header(token),
            json={"current_password": "wrong-pass", "new_password": "newsecret123"},
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Contraseña actual incorrecta"
    finally:
        await delete_user(email)


@pytest.mark.asyncio
async def test_change_password_requires_min_length(client):
    email = unique_email()
    await create_user(email=email)
    try:
        token = await login(client, email, PASSWORD)
        response = await client.post(
            "/auth/change-password",
            headers=await auth_header(token),
            json={"current_password": PASSWORD, "new_password": "short"},
        )
        assert response.status_code == 422
    finally:
        await delete_user(email)


@pytest.mark.asyncio
async def test_me_exposes_must_change_password(client):
    email = unique_email()
    await create_user(email=email, must_change_password=True)
    try:
        token = await login(client, email, PASSWORD)
        response = await client.get("/auth/me", headers=await auth_header(token))
        assert response.status_code == 200
        assert response.json()["must_change_password"] is True
    finally:
        await delete_user(email)