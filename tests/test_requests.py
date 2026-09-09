import pytest

from app.modules.requests.model import ApprovalStatus, RequestStatus
from tests.conftest import PASSWORD, auth_header, login


@pytest.fixture
async def sample_category(client, admin_user):
    token = await login(client, admin_user.email, PASSWORD)
    resp = await client.post(
        "/categories/",
        json={"name": "Software Setup", "requires_approval": True},
        headers=await auth_header(token),
    )
    return resp.json()


@pytest.fixture
async def sample_request(client, user_user):
    token = await login(client, user_user.email, PASSWORD)
    resp = await client.post(
        "/requests/",
        json={"description": "Need IDE installed"},
        headers=await auth_header(token),
    )
    return resp.json()


@pytest.mark.asyncio
async def test_create_request(client, user_user):
    token = await login(client, user_user.email, PASSWORD)
    response = await client.post(
        "/requests/",
        json={"description": "My computer won't start"},
        headers=await auth_header(token),
    )
    assert response.status_code == 201
    data = response.json()
    assert data["description"] == "My computer won't start"
    assert data["status"] == "PENDING"
    assert data["creator"]["email"] == user_user.email


@pytest.mark.asyncio
async def test_list_requests(client, user_user, agent_user, sample_request):
    # User lists
    token_user = await login(client, user_user.email, PASSWORD)
    resp_user = await client.get("/requests/", headers=await auth_header(token_user))
    assert resp_user.status_code == 200
    assert len(resp_user.json()) >= 1
    assert all(r["creator"]["email"] == user_user.email for r in resp_user.json() if "creator" in r)

    # Agent lists
    token_agent = await login(client, agent_user.email, PASSWORD)
    resp_agent = await client.get("/requests/", headers=await auth_header(token_agent))
    assert resp_agent.status_code == 200
    assert len(resp_agent.json()) >= 1


@pytest.mark.asyncio
async def test_classify_request(client, agent_user, sample_request, sample_category):
    token = await login(client, agent_user.email, PASSWORD)
    req_id = sample_request["id"]
    
    # Classify the request and assign to self
    response = await client.patch(
        f"/requests/{req_id}",
        json={"category_id": sample_category["id"], "assigned_to": agent_user.id},
        headers=await auth_header(token),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["category"]["id"] == sample_category["id"]
    assert data["assignee"]["id"] == agent_user.id

    # Check SLA was created
    sla_resp = await client.get(f"/requests/{req_id}/sla", headers=await auth_header(token))
    assert sla_resp.status_code == 200
    assert sla_resp.json()["responded_at"] is not None

    # Check Approval was created because category required it
    appr_resp = await client.get(f"/requests/{req_id}/approvals", headers=await auth_header(token))
    assert appr_resp.status_code == 200
    assert len(appr_resp.json()) == 1


@pytest.mark.asyncio
async def test_change_status(client, agent_user, sample_request):
    token = await login(client, agent_user.email, PASSWORD)
    req_id = sample_request["id"]
    
    response = await client.patch(
        f"/requests/{req_id}/status",
        json={"status": "IN_PROGRESS"},
        headers=await auth_header(token),
    )
    assert response.status_code == 200
    assert response.json()["status"] == "IN_PROGRESS"

    # Check history
    hist_resp = await client.get(f"/requests/{req_id}/history", headers=await auth_header(token))
    assert hist_resp.status_code == 200
    assert len(hist_resp.json()) > 0
    assert hist_resp.json()[-1]["action"] == "change_status"
    assert hist_resp.json()[-1]["new_value"] == "IN_PROGRESS"


@pytest.mark.asyncio
async def test_comments_visibility(client, user_user, agent_user, sample_request):
    req_id = sample_request["id"]
    token_user = await login(client, user_user.email, PASSWORD)
    token_agent = await login(client, agent_user.email, PASSWORD)

    # User adds public comment
    await client.post(
        f"/requests/{req_id}/comments",
        json={"content": "Public info", "is_internal": False},
        headers=await auth_header(token_user),
    )

    # Agent adds internal comment
    await client.post(
        f"/requests/{req_id}/comments",
        json={"content": "Internal note", "is_internal": True},
        headers=await auth_header(token_agent),
    )

    # User lists comments (should see 1)
    user_comments = await client.get(f"/requests/{req_id}/comments", headers=await auth_header(token_user))
    assert len(user_comments.json()) == 1
    assert user_comments.json()[0]["content"] == "Public info"

    # Agent lists comments (should see 2)
    agent_comments = await client.get(f"/requests/{req_id}/comments", headers=await auth_header(token_agent))
    assert len(agent_comments.json()) == 2
