import shutil
import uuid

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

import app.modules.customer.router as customer_router_module
from app.modules.customer.router import get_current_user_id, router as customer_router
from app.modules.customer.service import UPLOAD_DIR
from tests.conftest import (
    create_user_helper,
    delete_request_tree,
    delete_user_helper,
    unique_email,
)

UPLOAD_ROOT = UPLOAD_DIR


def _test_app() -> FastAPI:
    test_app = FastAPI()
    test_app.include_router(customer_router)
    return test_app


def _override_user(app: FastAPI, user_id: int) -> None:
    app.dependency_overrides[get_current_user_id] = lambda: user_id


@pytest.fixture
async def customer_client():
    app = _test_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac, app
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def _reset_rate_limits():
    customer_router_module._create_request_rate_limit_tracker.clear()
    customer_router_module._comment_rate_limit_tracker.clear()
    customer_router_module._attachment_rate_limit_tracker.clear()
    yield


@pytest.fixture
async def customer_user():
    email = unique_email()
    user = await create_user_helper(email=email, role_name="USER")
    yield user
    await delete_user_helper(email)


@pytest.fixture
async def other_user():
    email = unique_email()
    user = await create_user_helper(email=email, role_name="USER")
    yield user
    await delete_user_helper(email)


def _create(client, app, user_id, description=None):
    _override_user(app, user_id)
    return client.post(
        "/requests", json={"description": description or "No me funciona el VPN corporativo."}
    )


async def _cleanup_request(request_id: int) -> None:
    await delete_request_tree(request_id)
    dir_ = UPLOAD_ROOT / str(request_id)
    if dir_.exists():
        shutil.rmtree(dir_, ignore_errors=True)


async def test_create_request(customer_client, customer_user):
    client, app = customer_client
    resp = await _create(client, app, customer_user.id, None)
    assert resp.status_code == 201
    data = resp.json()
    assert data["id"]
    assert data["status"] == "NEW"
    assert data["created_by"] == customer_user.id
    assert data["category_id"] is None
    await _cleanup_request(data["id"])


async def test_create_request_requires_min_length(customer_client, customer_user):
    client, app = customer_client
    resp = await _create(client, app, customer_user.id, "corto")
    assert resp.status_code == 422


async def test_list_requests_paginates(customer_client, customer_user):
    client, app = customer_client
    created = []
    for i in range(3):
        resp = await _create(client, app, customer_user.id, None)
        assert resp.status_code == 201
        created.append(resp.json()["id"])
    try:
        resp = await client.get("/requests", params={"offset": 0, "limit": 2})
        assert resp.status_code == 200
        items = resp.json()
        assert len(items) == 2
        assert all(item["created_by"] == customer_user.id for item in items)
    finally:
        for request_id in created:
            await _cleanup_request(request_id)


async def test_get_request_detail_returns_nested_data(customer_client, customer_user):
    client, app = customer_client
    resp = await _create(client, app, customer_user.id, None)
    request_id = resp.json()["id"]
    try:
        comment = await client.post(
            f"/requests/{request_id}/comments", json={"content": "Probé con otra tarjeta."}
        )
        assert comment.status_code == 201
        assert comment.json()["is_internal"] is False

        detail = await client.get(f"/requests/{request_id}")
        assert detail.status_code == 200
        data = detail.json()
        assert data["id"] == request_id
        assert data["creator"]["email"] == customer_user.email
        assert len(data["comments"]) == 1
        assert data["comments"][0]["content"] == "Probé con otra tarjeta."
        assert data["comments"][0]["is_internal"] is False
        assert data["comments"][0]["user"]["email"] == customer_user.email
    finally:
        await _cleanup_request(request_id)


async def test_get_request_status(customer_client, customer_user):
    client, app = customer_client
    resp = await _create(client, app, customer_user.id, None)
    request_id = resp.json()["id"]
    try:
        resp = await client.get(f"/requests/{request_id}/status")
        assert resp.status_code == 200
        assert resp.json() == {"status": "NEW"}
    finally:
        await _cleanup_request(request_id)


async def test_get_request_priority_default(customer_client, customer_user):
    client, app = customer_client
    resp = await _create(client, app, customer_user.id, None)
    request_id = resp.json()["id"]
    try:
        resp = await client.get(f"/requests/{request_id}/priority")
        assert resp.status_code == 200
        assert resp.json() == {"id": None, "name": "PENDING", "level": None}
    finally:
        await _cleanup_request(request_id)


async def test_get_request_assignment_default(customer_client, customer_user):
    client, app = customer_client
    resp = await _create(client, app, customer_user.id, None)
    request_id = resp.json()["id"]
    try:
        resp = await client.get(f"/requests/{request_id}/assignment")
        assert resp.status_code == 200
        assert resp.json() == {"team": None, "assignee": None}
    finally:
        await _cleanup_request(request_id)


async def test_ownership_forbidden(customer_client, customer_user, other_user):
    client, app = customer_client
    resp = await _create(client, app, customer_user.id, None)
    request_id = resp.json()["id"]
    try:
        _override_user(app, other_user.id)
        resp = await client.get(f"/requests/{request_id}")
        assert resp.status_code == 403
    finally:
        await _cleanup_request(request_id)


async def test_not_found(customer_client, customer_user):
    client, app = customer_client
    _override_user(app, customer_user.id)
    resp = await client.get("/requests/999999")
    assert resp.status_code == 404


async def test_upload_attachment_success(customer_client, customer_user):
    client, app = customer_client
    resp = await _create(client, app, customer_user.id, None)
    request_id = resp.json()["id"]
    try:
        content = b"contenido de prueba"
        resp = await client.post(
            f"/requests/{request_id}/attachments",
            files={"file": ("nota.txt", content, "text/plain")},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["file_name"] == "nota.txt"
        assert data["request_id"] == request_id
        assert data["uploaded_by"] == customer_user.id

        detail = await client.get(f"/requests/{request_id}")
        assert len(detail.json()["attachments"]) == 1
    finally:
        await _cleanup_request(request_id)


async def test_upload_attachment_rejects_extension(customer_client, customer_user):
    client, app = customer_client
    resp = await _create(client, app, customer_user.id, None)
    request_id = resp.json()["id"]
    try:
        resp = await client.post(
            f"/requests/{request_id}/attachments",
            files={"file": ("malware.exe", b"pwned", "application/octet-stream")},
        )
        assert resp.status_code == 400
        assert "no está permitida" in resp.json()["detail"]
    finally:
        await _cleanup_request(request_id)


async def test_create_request_rate_limited(customer_client, customer_user):
    client, app = customer_client
    created = []
    try:
        for _ in range(6):
            resp = await _create(client, app, customer_user.id, None)
            if resp.status_code == 201:
                created.append(resp.json()["id"])
        assert len(created) == 5
        assert resp.status_code == 429
    finally:
        for request_id in created:
            await _cleanup_request(request_id)