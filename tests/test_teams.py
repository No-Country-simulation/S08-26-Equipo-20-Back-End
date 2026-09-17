import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete, select

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.main import app
from app.modules.requests.model import Request, RequestStatus
from app.modules.teams.model import Team
from app.modules.users.model import Role, User

PASSWORD = "secret123"


def unique_email() -> str:
    return f"team-{uuid.uuid4().hex[:8]}@test.com"


def unique_name() -> str:
    return f"Equipo {uuid.uuid4().hex[:8]}"


async def create_db_user(
    *,
    email: str,
    password: str = PASSWORD,
    role_name: str = "USER",
) -> User:
    async with SessionLocal() as session:
        role = await session.scalar(select(Role).where(Role.name == role_name))
        user = User(
            name="Test User",
            email=email,
            password_hash=hash_password(password),
            role_id=role.id,
        )
        session.add(user)
        await session.commit()
        return user


async def delete_user(email: str) -> None:
    async with SessionLocal() as session:
        await session.execute(delete(User).where(User.email == email))
        await session.commit()


async def create_team(name: str, description: str | None = None) -> Team:
    async with SessionLocal() as session:
        team = Team(name=name, description=description)
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


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_create_team_success(client):
    admin_email, headers = await admin_token(client)
    name = unique_name()
    try:
        response = await client.post(
            "/teams", headers=headers, json={"name": name, "description": "Soporte"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == name
        assert data["description"] == "Soporte"

        team_id = data["id"]
        response = await client.get("/teams", headers=headers)
        assert any(item["id"] == team_id for item in response.json()["items"])
        await delete_team(team_id)
    finally:
        await delete_user(admin_email)


@pytest.mark.asyncio
async def test_create_team_duplicate_name(client):
    admin_email, headers = await admin_token(client)
    name = unique_name()
    team = await create_team(name)
    try:
        response = await client.post(
            "/teams", headers=headers, json={"name": name}
        )
        assert response.status_code == 409
        assert response.json()["detail"] == "Ya existe un equipo con ese nombre"
    finally:
        await delete_team(team.id)
        await delete_user(admin_email)


@pytest.mark.asyncio
async def test_list_teams_requires_auth(client):
    response = await client.get("/teams")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_team(client):
    admin_email, headers = await admin_token(client)
    team = await create_team(unique_name(), "Atención")
    try:
        response = await client.get(f"/teams/{team.id}", headers=headers)
        assert response.status_code == 200
        assert response.json()["name"] == team.name
        assert response.json()["description"] == "Atención"
    finally:
        await delete_team(team.id)
        await delete_user(admin_email)


@pytest.mark.asyncio
async def test_get_team_not_found(client):
    admin_email, headers = await admin_token(client)
    try:
        response = await client.get("/teams/999999", headers=headers)
        assert response.status_code == 404
        assert response.json()["detail"] == "Equipo no encontrado"
    finally:
        await delete_user(admin_email)


@pytest.mark.asyncio
async def test_update_team(client):
    admin_email, headers = await admin_token(client)
    team = await create_team(unique_name())
    new_name = unique_name()
    try:
        response = await client.patch(
            f"/teams/{team.id}",
            headers=headers,
            json={"name": new_name, "description": "Administración"},
        )
        assert response.status_code == 200
        assert response.json()["name"] == new_name
        assert response.json()["description"] == "Administración"

        response = await client.patch(
            f"/teams/{team.id}", headers=headers, json={"description": None}
        )
        assert response.status_code == 200
        assert response.json()["description"] is None
    finally:
        await delete_team(team.id)
        await delete_user(admin_email)


@pytest.mark.asyncio
async def test_update_team_duplicate_name(client):
    admin_email, headers = await admin_token(client)
    team_a = await create_team(unique_name())
    team_b = await create_team(unique_name())
    try:
        response = await client.patch(
            f"/teams/{team_b.id}",
            headers=headers,
            json={"name": team_a.name},
        )
        assert response.status_code == 409
    finally:
        await delete_team(team_a.id)
        await delete_team(team_b.id)
        await delete_user(admin_email)


@pytest.mark.asyncio
async def test_non_admin_cannot_create_team(client):
    user_email = unique_email()
    await create_db_user(email=user_email)
    token = await login(client, user_email, PASSWORD)
    try:
        response = await client.post(
            "/teams",
            headers=auth_header(token),
            json={"name": unique_name()},
        )
        assert response.status_code == 403
        assert (
            response.json()["detail"]
            == "No tiene permisos para realizar esta acción"
        )
    finally:
        await delete_user(user_email)


@pytest.mark.asyncio
async def test_delete_team_without_users(client):
    admin_email, headers = await admin_token(client)
    team = await create_team(unique_name())
    try:
        response = await client.delete(f"/teams/{team.id}", headers=headers)
        assert response.status_code == 204

        response = await client.get(f"/teams/{team.id}", headers=headers)
        assert response.status_code == 404
    finally:
        await delete_user(admin_email)


@pytest.mark.asyncio
async def test_delete_team_with_users_blocked(client):
    admin_email, headers = await admin_token(client)
    team = await create_team(unique_name())
    user_email = unique_email()
    user = await create_db_user(email=user_email)
    try:
        async with SessionLocal() as session:
            user = await session.get(User, user.id)
            user.team_id = team.id
            await session.commit()

        response = await client.delete(f"/teams/{team.id}", headers=headers)
        assert response.status_code == 400
        assert (
            response.json()["detail"]
            == "No se puede eliminar un equipo con usuarios o solicitudes asociadas"
        )
    finally:
        await delete_user(user_email)
        await delete_team(team.id)
        await delete_user(admin_email)


@pytest.mark.asyncio
async def test_delete_team_with_requests_blocked(client):
    admin_email, headers = await admin_token(client)
    team = await create_team(unique_name())
    creator_email = unique_email()
    creator = await create_db_user(email=creator_email)
    request_id = None
    try:
        async with SessionLocal() as session:
            request = Request(
                description="Solicitud de prueba",
                status=RequestStatus.NEW,
                team_id=team.id,
                created_by=creator.id,
            )
            session.add(request)
            await session.commit()
            request_id = request.id

        response = await client.delete(f"/teams/{team.id}", headers=headers)
        assert response.status_code == 400
        assert (
            response.json()["detail"]
            == "No se puede eliminar un equipo con usuarios o solicitudes asociadas"
        )
    finally:
        if request_id is not None:
            async with SessionLocal() as session:
                await session.execute(delete(Request).where(Request.id == request_id))
                await session.commit()
        await delete_user(creator_email)
        await delete_team(team.id)
        await delete_user(admin_email)