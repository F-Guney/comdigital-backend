import pytest
from httpx import AsyncClient

from tests.conftest import auth_headers


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    resp = await client.post(
        "/api/users/register",
        json={
            "email": "new@example.com",
            "password": "securepass123",
            "first_name": "John",
            "last_name": "Doe",
        },
    )

    assert resp.status_code == 201

    body = resp.json()

    assert body["success"] is True
    assert body["data"]["email"] == "new@example.com"
    assert "password" not in body["data"]


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    payload = {
        "email": "dup@example.com",
        "password": "securepass123",
        "first_name": "A",
        "last_name": "B",
    }
    await client.post("/api/users/register", json=payload)
    resp = await client.post("/api/users/register", json=payload)

    assert resp.status_code == 409
    assert resp.json()["error"] == "DUPLICATE_EMAIL"


@pytest.mark.asyncio
async def test_register_invalid_email(client: AsyncClient):
    resp = await client.post(
        "/api/users/register",
        json={
            "email": "not-an-email",
            "password": "securepass123",
            "first_name": "A",
            "last_name": "B",
        },
    )

    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_get_profile_success(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/users/profile", headers=auth_headers)
    assert resp.status_code == 200

    data = resp.json()["data"]
    assert data["email"] == "fixture@example.com"


@pytest.mark.asyncio
async def test_update_profile_success(client: AsyncClient, auth_headers: dict):
    resp = await client.put(
        "/api/users/profile",
        headers=auth_headers,
        json={"first_name": "Updated", "last_name": "Name"},
    )

    assert resp.status_code == 200
    assert resp.json()["data"]["first_name"] == "Updated"
    assert resp.json()["data"]["last_name"] == "Name"


@pytest.mark.asyncio
async def test_get_profile_unauthorized(client: AsyncClient):
    resp = await client.get("/api/users/profile")
    assert resp.status_code in (401, 403)
