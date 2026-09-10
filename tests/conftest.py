import uuid
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete, select

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.main import app
from app.modules.users.model import Role, User

PASSWORD = "secret123"


def unique_email() -> str:
    return f"user-{uuid.uuid4().hex[:8]}@test.com"


async def create_user_helper(
    email: str,
    password: str = PASSWORD,
    role_name: str = "USER",
    active: bool = True,
    must_change_password: bool = False,
) -> User:
    async with SessionLocal() as session:
        role = await session.scalar(select(Role).where(Role.name == role_name))
        if role is None:
            role = Role(name=role_name)
            session.add(role)
            await session.commit()
        user = User(
            name=f"Test {role_name}",
            email=email,
            password_hash=hash_password(password),
            role_id=role.id,
            is_active=active,
            must_change_password=must_change_password,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


async def delete_user_helper(email: str) -> None:
    async with SessionLocal() as session:
        await session.execute(delete(User).where(User.email == email))
        await session.commit()


async def login_helper(client: AsyncClient, email: str, password: str) -> str:
    response = await client.post(
        "/auth/login", json={"email": email, "password": password}
    )
    assert response.status_code == 200
    return response.json()["access_token"]


async def auth_header_helper(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def user_user():
    email = unique_email()
    user = await create_user_helper(email=email, role_name="USER")
    yield user
    await delete_user_helper(email)


@pytest.fixture
async def agent_user():
    email = unique_email()
    user = await create_user_helper(email=email, role_name="AGENT")
    yield user
    await delete_user_helper(email)


@pytest.fixture
async def admin_user():
    email = unique_email()
    user = await create_user_helper(email=email, role_name="ADMIN")
    yield user
    await delete_user_helper(email)
