import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete, select

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.main import app
from app.modules.teams.model import Team
from app.modules.users.model import Role, User

PASSWORD = "secret123"


def unique_email() -> str:
    return f"user-{uuid.uuid4().hex[:8]}@test.com"


def unique_name() -> str:
    return f"Equipo {uuid.uuid4().hex[:8]}"


async def get_role_id(role_name: str) -> int:
    async with SessionLocal() as session:
        role = await session.scalar(select(Role).where(Role.name == role_name))
        return role.id


async def create_db_user(
    *,
    email: str,
    password: str = PASSWORD,
    role_name: str = "USER",
    active: bool = True,
    name: str = "Test User",
) -> User:
    async with SessionLocal() as session:
        role = await session.scalar(select(Role).where(Role.name == role_name))
        user = User(
            name=name,
            email=email,
            password_hash=hash_password(password),
            role_id=role.id,
            is_active=active,
        )
        session.add(user)
        await session.commit()
        return user


async def delete_user(email: str) -> None:
    async with SessionLocal() as session:
        await session.execute(delete(User).where(User.email == email))
        await session.commit()


async def create_team(name: str) -> Team:
    async with SessionLocal() as session:
        team = Team(name=name)
        session.add(team)
        await session.commit()
        return team


async def delete_team(team_id: int) -> None:
    async with SessionLocal() as session:
        await session.execute(delete(Team).where(Team.id == team_id))
        await session.commit()


async def login(client: AsyncClient, email: str, password: str) -> str:
    response = await client.post(
        "/auth/login", json={"email": email, "password": password}
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


async def admin_token(client: AsyncClient) -> tuple[str, str]:
    email = unique_email()
    await create_db_user(email=email, role_name="ADMIN")
    token = await login(client, email, PASSWORD)
    return email, auth_header(token)


async def user_payload(role_id: int | None = None) -> dict:
    if role_id is None:
        role_id = await get_role_id("USER")
    return {
        "name": "Nuevo Usuario",
        "email": unique_email(),
        "role_id": role_id,
        "password": PASSWORD,
    }


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_create_user_success(client):
    admin_email, headers = await admin_token(client)
    payload = await user_payload()
    try:
        response = await client.post("/users", headers=headers, json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["user"]["email"] == payload["email"]
        assert data["user"]["role"] == "USER"
        assert data["user"]["must_change_password"] is False
        assert data["temporary_password"] is None

        login_response = await client.post(
            "/auth/login", json={"email": payload["email"], "password": PASSWORD}
        )
        assert login_response.status_code == 200
    finally:
        await delete_user(payload["email"])
        await delete_user(admin_email)


@pytest.mark.asyncio
async def test_create_user_generates_temporary_password(client):
    admin_email, headers = await admin_token(client)
    payload = await user_payload()
    payload.pop("password")
    try:
        response = await client.post("/users", headers=headers, json=payload)
        assert response.status_code == 201
        data = response.json()
        temp = data["temporary_password"]
        assert temp and len(temp) == 12
        assert data["user"]["must_change_password"] is True

        login_response = await client.post(
            "/auth/login", json={"email": payload["email"], "password": temp}
        )
        assert login_response.status_code == 200
    finally:
        await delete_user(payload["email"])
        await delete_user(admin_email)


@pytest.mark.asyncio
async def test_create_user_duplicate_email(client):
    admin_email, headers = await admin_token(client)
    payload = await user_payload()
    await create_db_user(email=payload["email"])
    try:
        response = await client.post("/users", headers=headers, json=payload)
        assert response.status_code == 409
        assert response.json()["detail"] == "Ya existe un usuario con ese email"
    finally:
        await delete_user(payload["email"])
        await delete_user(admin_email)


@pytest.mark.asyncio
async def test_create_user_invalid_role(client):
    admin_email, headers = await admin_token(client)
    payload = await user_payload(role_id=999999)
    try:
        response = await client.post("/users", headers=headers, json=payload)
        assert response.status_code == 400
        assert response.json()["detail"] == "Rol no válido"
    finally:
        await delete_user(admin_email)


@pytest.mark.asyncio
async def test_create_user_invalid_team(client):
    admin_email, headers = await admin_token(client)
    payload = await user_payload()
    payload["team_id"] = 999999
    try:
        response = await client.post("/users", headers=headers, json=payload)
        assert response.status_code == 400
        assert response.json()["detail"] == "Equipo no válido"
    finally:
        await delete_user(admin_email)


@pytest.mark.asyncio
async def test_list_users_requires_auth(client):
    response = await client.get("/users")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_users_with_filters(client):
    admin_email, headers = await admin_token(client)
    user_email = unique_email()
    await create_db_user(email=user_email, role_name="USER", name="Filtrable Ejemplo")
    try:
        response = await client.get(
            "/users", headers=headers, params={"search": "Filtrable"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        assert any(item["email"] == user_email for item in data["items"])

        response = await client.get(
            "/users", headers=headers, params={"role": "AGENT"}
        )
        assert response.status_code == 200
        assert all(item["role"] == "AGENT" for item in response.json()["items"])
    finally:
        await delete_user(user_email)
        await delete_user(admin_email)


@pytest.mark.asyncio
async def test_get_user(client):
    admin_email, headers = await admin_token(client)
    user_email = unique_email()
    user = await create_db_user(email=user_email)
    try:
        response = await client.get(f"/users/{user.id}", headers=headers)
        assert response.status_code == 200
        assert response.json()["email"] == user_email
    finally:
        await delete_user(user_email)
        await delete_user(admin_email)


@pytest.mark.asyncio
async def test_get_user_not_found(client):
    admin_email, headers = await admin_token(client)
    try:
        response = await client.get("/users/999999", headers=headers)
        assert response.status_code == 404
        assert response.json()["detail"] == "Usuario no encontrado"
    finally:
        await delete_user(admin_email)


@pytest.mark.asyncio
async def test_update_user_role(client):
    admin_email, headers = await admin_token(client)
    user_email = unique_email()
    user = await create_db_user(email=user_email)
    admin_role_id = await get_role_id("ADMIN")
    try:
        response = await client.patch(
            f"/users/{user.id}",
            headers=headers,
            json={"role_id": admin_role_id},
        )
        assert response.status_code == 200
        assert response.json()["role"] == "ADMIN"
    finally:
        await delete_user(user_email)
        await delete_user(admin_email)


@pytest.mark.asyncio
async def test_update_user_assign_and_remove_team(client):
    admin_email, headers = await admin_token(client)
    user_email = unique_email()
    user = await create_db_user(email=user_email)
    team = await create_team(unique_name())
    try:
        response = await client.patch(
            f"/users/{user.id}", headers=headers, json={"team_id": team.id}
        )
        assert response.status_code == 200
        assert response.json()["team_id"] == team.id

        response = await client.patch(
            f"/users/{user.id}", headers=headers, json={"team_id": None}
        )
        assert response.status_code == 200
        assert response.json()["team_id"] is None
    finally:
        await delete_user(user_email)
        await delete_team(team.id)
        await delete_user(admin_email)


@pytest.mark.asyncio
async def test_update_user_invalid_role(client):
    admin_email, headers = await admin_token(client)
    user_email = unique_email()
    user = await create_db_user(email=user_email)
    try:
        response = await client.patch(
            f"/users/{user.id}", headers=headers, json={"role_id": 999999}
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Rol no válido"
    finally:
        await delete_user(user_email)
        await delete_user(admin_email)


@pytest.mark.asyncio
async def test_non_admin_cannot_create_user(client):
    user_email = unique_email()
    await create_db_user(email=user_email)
    token = await login(client, user_email, PASSWORD)
    try:
        payload = await user_payload()
        response = await client.post("/users", headers=auth_header(token), json=payload)
        assert response.status_code == 403
        assert (
            response.json()["detail"]
            == "No tiene permisos para realizar esta acción"
        )
    finally:
        await delete_user(user_email)


@pytest.mark.asyncio
async def test_admin_cannot_deactivate_self(client):
    admin_email, headers = await admin_token(client)
    try:
        me = await client.get("/auth/me", headers=headers)
        my_id = me.json()["id"]
        response = await client.patch(
            f"/users/{my_id}", headers=headers, json={"is_active": False}
        )
        assert response.status_code == 400
        assert (
            response.json()["detail"]
            == "Un administrador no puede desactivarse a sí mismo"
        )
    finally:
        await delete_user(admin_email)


@pytest.mark.asyncio
async def test_admin_can_deactivate_another_admin(client):
    admin_email, headers = await admin_token(client)
    other_admin_email = unique_email()
    other_admin = await create_db_user(email=other_admin_email, role_name="ADMIN")
    try:
        response = await client.patch(
            f"/users/{other_admin.id}", headers=headers, json={"is_active": False}
        )
        assert response.status_code == 200
        assert response.json()["is_active"] is False

        login_response = await client.post(
            "/auth/login", json={"email": other_admin_email, "password": PASSWORD}
        )
        assert login_response.status_code == 401
    finally:
        await delete_user(other_admin_email)
        await delete_user(admin_email)


@pytest.mark.asyncio
async def test_delete_user_soft_deactivate(client):
    admin_email, headers = await admin_token(client)
    user_email = unique_email()
    user = await create_db_user(email=user_email)
    try:
        response = await client.delete(f"/users/{user.id}", headers=headers)
        assert response.status_code == 200
        assert response.json()["is_active"] is False

        login_response = await client.post(
            "/auth/login", json={"email": user_email, "password": PASSWORD}
        )
        assert login_response.status_code == 401
    finally:
        await delete_user(user_email)
        await delete_user(admin_email)