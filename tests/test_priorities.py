import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete, select

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.main import app
from app.modules.priorities.model import Prioritie
from app.modules.requests.model import Request, RequestStatus
from app.modules.users.model import Role, User

PASSWORD = "secret123"


def unique_email() -> str:
    return f"priority-{uuid.uuid4().hex[:8]}@test.com"


def unique_name() -> str:
    return f"Prioridad {uuid.uuid4().hex[:8]}"


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


async def create_priority(name: str, level: int) -> Prioritie:
    async with SessionLocal() as session:
        priority = Prioritie(name=name, level=level)
        session.add(priority)
        await session.commit()
        return priority


async def delete_priority(priority_id: int) -> None:
    async with SessionLocal() as session:
        await session.execute(delete(Prioritie).where(Prioritie.id == priority_id))
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
async def test_create_priority_success(client):
    admin_email, headers = await admin_token(client)
    name = unique_name()
    try:
        response = await client.post(
            "/priorities", headers=headers, json={"name": name, "level": 1}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == name
        assert data["level"] == 1

        priority_id = data["id"]
        response = await client.get("/priorities", headers=headers)
        assert any(item["id"] == priority_id for item in response.json()["items"])
        await delete_priority(priority_id)
    finally:
        await delete_user(admin_email)


@pytest.mark.asyncio
async def test_create_priority_duplicate_name(client):
    admin_email, headers = await admin_token(client)
    name = unique_name()
    priority = await create_priority(name, 1)
    try:
        response = await client.post(
            "/priorities", headers=headers, json={"name": name, "level": 2}
        )
        assert response.status_code == 409
        assert response.json()["detail"] == "Ya existe una prioridad con ese nombre"
    finally:
        await delete_priority(priority.id)
        await delete_user(admin_email)


@pytest.mark.asyncio
async def test_create_priority_duplicate_level(client):
    admin_email, headers = await admin_token(client)
    priority = await create_priority(unique_name(), 1)
    try:
        response = await client.post(
            "/priorities",
            headers=headers,
            json={"name": unique_name(), "level": 1},
        )
        assert response.status_code == 409
        assert response.json()["detail"] == "Ya existe una prioridad con ese nivel"
    finally:
        await delete_priority(priority.id)
        await delete_user(admin_email)


@pytest.mark.asyncio
async def test_create_priority_invalid_level(client):
    admin_email, headers = await admin_token(client)
    try:
        response = await client.post(
            "/priorities",
            headers=headers,
            json={"name": unique_name(), "level": 0},
        )
        assert response.status_code == 422
    finally:
        await delete_user(admin_email)


@pytest.mark.asyncio
async def test_list_priorities_requires_auth(client):
    response = await client.get("/priorities")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_priority(client):
    admin_email, headers = await admin_token(client)
    priority = await create_priority(unique_name(), 3)
    try:
        response = await client.get(f"/priorities/{priority.id}", headers=headers)
        assert response.status_code == 200
        assert response.json()["name"] == priority.name
        assert response.json()["level"] == 3
    finally:
        await delete_priority(priority.id)
        await delete_user(admin_email)


@pytest.mark.asyncio
async def test_get_priority_not_found(client):
    admin_email, headers = await admin_token(client)
    try:
        response = await client.get("/priorities/999999", headers=headers)
        assert response.status_code == 404
        assert response.json()["detail"] == "Prioridad no encontrada"
    finally:
        await delete_user(admin_email)


@pytest.mark.asyncio
async def test_update_priority(client):
    admin_email, headers = await admin_token(client)
    priority = await create_priority(unique_name(), 1)
    new_name = unique_name()
    try:
        response = await client.patch(
            f"/priorities/{priority.id}",
            headers=headers,
            json={"name": new_name, "level": 2},
        )
        assert response.status_code == 200
        assert response.json()["name"] == new_name
        assert response.json()["level"] == 2
    finally:
        await delete_priority(priority.id)
        await delete_user(admin_email)


@pytest.mark.asyncio
async def test_update_priority_duplicate_name(client):
    admin_email, headers = await admin_token(client)
    priority_a = await create_priority(unique_name(), 1)
    priority_b = await create_priority(unique_name(), 2)
    try:
        response = await client.patch(
            f"/priorities/{priority_b.id}",
            headers=headers,
            json={"name": priority_a.name},
        )
        assert response.status_code == 409
    finally:
        await delete_priority(priority_a.id)
        await delete_priority(priority_b.id)
        await delete_user(admin_email)


@pytest.mark.asyncio
async def test_update_priority_duplicate_level(client):
    admin_email, headers = await admin_token(client)
    priority_a = await create_priority(unique_name(), 1)
    priority_b = await create_priority(unique_name(), 2)
    try:
        response = await client.patch(
            f"/priorities/{priority_b.id}",
            headers=headers,
            json={"level": 1},
        )
        assert response.status_code == 409
        assert response.json()["detail"] == "Ya existe una prioridad con ese nivel"
    finally:
        await delete_priority(priority_a.id)
        await delete_priority(priority_b.id)
        await delete_user(admin_email)


@pytest.mark.asyncio
async def test_non_admin_cannot_create_priority(client):
    user_email = unique_email()
    await create_db_user(email=user_email)
    token = await login(client, user_email, PASSWORD)
    try:
        response = await client.post(
            "/priorities",
            headers=auth_header(token),
            json={"name": unique_name(), "level": 1},
        )
        assert response.status_code == 403
        assert (
            response.json()["detail"]
            == "No tiene permisos para realizar esta acción"
        )
    finally:
        await delete_user(user_email)


@pytest.mark.asyncio
async def test_delete_priority_without_requests(client):
    admin_email, headers = await admin_token(client)
    priority = await create_priority(unique_name(), 1)
    try:
        response = await client.delete(f"/priorities/{priority.id}", headers=headers)
        assert response.status_code == 204

        response = await client.get(f"/priorities/{priority.id}", headers=headers)
        assert response.status_code == 404
    finally:
        await delete_user(admin_email)


@pytest.mark.asyncio
async def test_delete_priority_with_requests_blocked(client):
    admin_email, headers = await admin_token(client)
    priority = await create_priority(unique_name(), 1)
    creator_email = unique_email()
    creator = await create_db_user(email=creator_email)
    request_id = None
    try:
        async with SessionLocal() as session:
            request = Request(
                description="Solicitud de prueba",
                status=RequestStatus.NEW,
                priority_id=priority.id,
                created_by=creator.id,
            )
            session.add(request)
            await session.commit()
            request_id = request.id

        response = await client.delete(f"/priorities/{priority.id}", headers=headers)
        assert response.status_code == 400
        assert (
            response.json()["detail"]
            == "No se puede eliminar una prioridad con solicitudes asociadas"
        )
    finally:
        if request_id is not None:
            async with SessionLocal() as session:
                await session.execute(delete(Request).where(Request.id == request_id))
                await session.commit()
        await delete_user(creator_email)
        await delete_priority(priority.id)
        await delete_user(admin_email)