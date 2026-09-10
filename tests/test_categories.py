import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete, select

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.main import app
from app.modules.categories.model import Categorie
from app.modules.requests.model import Request, RequestStatus
from app.modules.users.model import Role, User

PASSWORD = "secret123"


def unique_email() -> str:
    return f"category-{uuid.uuid4().hex[:8]}@test.com"


def unique_name() -> str:
    return f"Categoría {uuid.uuid4().hex[:8]}"


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


async def create_category(name: str, description: str | None = None) -> Categorie:
    async with SessionLocal() as session:
        category = Categorie(name=name, description=description)
        session.add(category)
        await session.commit()
        return category


async def delete_category(category_id: int) -> None:
    async with SessionLocal() as session:
        await session.execute(delete(Categorie).where(Categorie.id == category_id))
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
async def test_create_category_success(client):
    admin_email, headers = await admin_token(client)
    name = unique_name()
    try:
        response = await client.post(
            "/categories",
            headers=headers,
            json={"name": name, "description": "Hardware", "requires_approval": True},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == name
        assert data["description"] == "Hardware"
        assert data["requires_approval"] is True

        category_id = data["id"]
        response = await client.get("/categories", headers=headers)
        assert any(item["id"] == category_id for item in response.json()["items"])
        await delete_category(category_id)
    finally:
        await delete_user(admin_email)


@pytest.mark.asyncio
async def test_create_category_defaults_requires_approval_false(client):
    admin_email, headers = await admin_token(client)
    name = unique_name()
    try:
        response = await client.post(
            "/categories", headers=headers, json={"name": name}
        )
        assert response.status_code == 201
        assert response.json()["requires_approval"] is False
        assert response.json()["description"] is None
        await delete_category(response.json()["id"])
    finally:
        await delete_user(admin_email)


@pytest.mark.asyncio
async def test_create_category_duplicate_name(client):
    admin_email, headers = await admin_token(client)
    name = unique_name()
    category = await create_category(name)
    try:
        response = await client.post(
            "/categories", headers=headers, json={"name": name}
        )
        assert response.status_code == 409
        assert response.json()["detail"] == "Ya existe una categoría con ese nombre"
    finally:
        await delete_category(category.id)
        await delete_user(admin_email)


@pytest.mark.asyncio
async def test_list_categories_requires_auth(client):
    response = await client.get("/categories")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_category(client):
    admin_email, headers = await admin_token(client)
    category = await create_category(unique_name(), "Soporte")
    try:
        response = await client.get(f"/categories/{category.id}", headers=headers)
        assert response.status_code == 200
        assert response.json()["name"] == category.name
        assert response.json()["description"] == "Soporte"
    finally:
        await delete_category(category.id)
        await delete_user(admin_email)


@pytest.mark.asyncio
async def test_get_category_not_found(client):
    admin_email, headers = await admin_token(client)
    try:
        response = await client.get("/categories/999999", headers=headers)
        assert response.status_code == 404
        assert response.json()["detail"] == "Categoría no encontrada"
    finally:
        await delete_user(admin_email)


@pytest.mark.asyncio
async def test_update_category(client):
    admin_email, headers = await admin_token(client)
    category = await create_category(unique_name())
    new_name = unique_name()
    try:
        response = await client.patch(
            f"/categories/{category.id}",
            headers=headers,
            json={
                "name": new_name,
                "description": "Infraestructura",
                "requires_approval": True,
            },
        )
        assert response.status_code == 200
        assert response.json()["name"] == new_name
        assert response.json()["description"] == "Infraestructura"
        assert response.json()["requires_approval"] is True

        response = await client.patch(
            f"/categories/{category.id}",
            headers=headers,
            json={"requires_approval": False},
        )
        assert response.status_code == 200
        assert response.json()["requires_approval"] is False
    finally:
        await delete_category(category.id)
        await delete_user(admin_email)


@pytest.mark.asyncio
async def test_update_category_duplicate_name(client):
    admin_email, headers = await admin_token(client)
    category_a = await create_category(unique_name())
    category_b = await create_category(unique_name())
    try:
        response = await client.patch(
            f"/categories/{category_b.id}",
            headers=headers,
            json={"name": category_a.name},
        )
        assert response.status_code == 409
    finally:
        await delete_category(category_a.id)
        await delete_category(category_b.id)
        await delete_user(admin_email)


@pytest.mark.asyncio
async def test_non_admin_cannot_create_category(client):
    user_email = unique_email()
    await create_db_user(email=user_email)
    token = await login(client, user_email, PASSWORD)
    try:
        response = await client.post(
            "/categories",
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
async def test_delete_category_without_requests(client):
    admin_email, headers = await admin_token(client)
    category = await create_category(unique_name())
    try:
        response = await client.delete(f"/categories/{category.id}", headers=headers)
        assert response.status_code == 204

        response = await client.get(f"/categories/{category.id}", headers=headers)
        assert response.status_code == 404
    finally:
        await delete_user(admin_email)


@pytest.mark.asyncio
async def test_delete_category_with_requests_blocked(client):
    admin_email, headers = await admin_token(client)
    category = await create_category(unique_name())
    creator_email = unique_email()
    creator = await create_db_user(email=creator_email)
    request_id = None
    try:
        async with SessionLocal() as session:
            request = Request(
                description="Solicitud de prueba",
                status=RequestStatus.NEW,
                category_id=category.id,
                created_by=creator.id,
            )
            session.add(request)
            await session.commit()
            request_id = request.id

        response = await client.delete(f"/categories/{category.id}", headers=headers)
        assert response.status_code == 400
        assert (
            response.json()["detail"]
            == "No se puede eliminar una categoría con solicitudes asociadas"
        )
    finally:
        if request_id is not None:
            async with SessionLocal() as session:
                await session.execute(delete(Request).where(Request.id == request_id))
                await session.commit()
        await delete_user(creator_email)
        await delete_category(category.id)
        await delete_user(admin_email)