import pytest
from httpx import AsyncClient

SAMPLE_ITEM = {
    "name": "Test Item",
    "description": "A test item",
    "category": "electronics",
    "status": "active",
}


async def _create_item(client: AsyncClient, headers: dict, **overrides) -> dict:
    payload = {**SAMPLE_ITEM, **overrides}
    resp = await client.post("/api/items/", json=payload, headers=headers)

    return resp.json()["data"]


@pytest.mark.asyncio
async def test_create_item(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/items/", json=SAMPLE_ITEM, headers=auth_headers)
    assert resp.status_code == 201

    data = resp.json()["data"]
    assert data["name"] == "Test Item"
    assert data["category"] == "electronics"


@pytest.mark.asyncio
async def test_create_item_unauthorized(client: AsyncClient):
    resp = await client.post("/api/items/", json=SAMPLE_ITEM)
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_get_item_by_id(client: AsyncClient, auth_headers: dict):
    created = await _create_item(client, auth_headers)
    resp = await client.get(f"/api/items/{created['id']}", headers=auth_headers)

    assert resp.status_code == 200
    assert resp.json()["data"]["name"] == "Test Item"


@pytest.mark.asyncio
async def test_get_item_not_found(client: AsyncClient, auth_headers: dict):
    fake_id = "00000000-0000-0000-0000-000000000000"
    resp = await client.get(f"/api/items/{fake_id}", headers=auth_headers)

    assert resp.status_code == 404
    assert resp.json()["error"] == "NOT_FOUND"
