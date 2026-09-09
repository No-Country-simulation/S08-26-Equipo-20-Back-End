import pytest

from tests.conftest import PASSWORD, auth_header, login

# --- Categories ---


@pytest.mark.asyncio
async def test_create_category_admin(client, admin_user):
    token = await login(client, admin_user.email, PASSWORD)
    response = await client.post(
        "/categories/",
        json={"name": "Hardware", "description": "Issues with physical devices"},
        headers=await auth_header(token),
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Hardware"


@pytest.mark.asyncio
async def test_create_category_forbidden_for_user(client, user_user):
    token = await login(client, user_user.email, PASSWORD)
    response = await client.post(
        "/categories/",
        json={"name": "Software"},
        headers=await auth_header(token),
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_list_categories(client, user_user, admin_user):
    # Admin creates one
    token_admin = await login(client, admin_user.email, PASSWORD)
    await client.post(
        "/categories/",
        json={"name": "Network"},
        headers=await auth_header(token_admin),
    )
    
    # User lists
    token_user = await login(client, user_user.email, PASSWORD)
    response = await client.get("/categories/", headers=await auth_header(token_user))
    assert response.status_code == 200
    assert len(response.json()) >= 1
    assert any(c["name"] == "Network" for c in response.json())


# --- Priorities ---


@pytest.mark.asyncio
async def test_create_priority_admin(client, admin_user):
    token = await login(client, admin_user.email, PASSWORD)
    response = await client.post(
        "/priorities/",
        json={"name": "High", "level": 1},
        headers=await auth_header(token),
    )
    assert response.status_code == 201
    assert response.json()["name"] == "High"


@pytest.mark.asyncio
async def test_create_priority_duplicate_level(client, admin_user):
    token = await login(client, admin_user.email, PASSWORD)
    await client.post(
        "/priorities/",
        json={"name": "P1", "level": 10},
        headers=await auth_header(token),
    )
    response = await client.post(
        "/priorities/",
        json={"name": "P2", "level": 10},
        headers=await auth_header(token),
    )
    assert response.status_code == 409


# --- Teams ---


@pytest.mark.asyncio
async def test_create_team_admin(client, admin_user):
    token = await login(client, admin_user.email, PASSWORD)
    response = await client.post(
        "/teams/",
        json={"name": "IT Support"},
        headers=await auth_header(token),
    )
    assert response.status_code == 201
    assert response.json()["name"] == "IT Support"


@pytest.mark.asyncio
async def test_update_team(client, admin_user):
    token = await login(client, admin_user.email, PASSWORD)
    create_resp = await client.post(
        "/teams/",
        json={"name": "HR"},
        headers=await auth_header(token),
    )
    team_id = create_resp.json()["id"]

    response = await client.patch(
        f"/teams/{team_id}",
        json={"name": "Human Resources"},
        headers=await auth_header(token),
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Human Resources"
