import uuid

import pytest


@pytest.mark.asyncio
async def test_register_and_login(client):
    email = f"test-{uuid.uuid4().hex[:8]}@example.com"
    register_resp = await client.post(
        "/api/v1/auth/register",
        json={"full_name": "Test User", "email": email, "password": "TestPass123"},
    )
    assert register_resp.status_code == 201
    body = register_resp.json()
    assert body["roles"] == ["CITIZEN"]

    login_resp = await client.post("/api/v1/auth/login", json={"email": email, "password": "TestPass123"})
    assert login_resp.status_code == 200
    tokens = login_resp.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens


@pytest.mark.asyncio
async def test_login_wrong_password_fails(client):
    email = f"test-{uuid.uuid4().hex[:8]}@example.com"
    await client.post("/api/v1/auth/register", json={"full_name": "Test User", "email": email, "password": "TestPass123"})

    resp = await client.post("/api/v1/auth/login", json={"email": email, "password": "WrongPassword"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me_requires_auth(client):
    resp = await client.get("/api/v1/auth/me")
    assert resp.status_code == 401
