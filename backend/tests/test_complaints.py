import uuid

import pytest
from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.models.complaint import ComplaintCategory


async def _ensure_category(code: str, module_id: str = "civic") -> None:
    async with AsyncSessionLocal() as db:
        existing = (await db.execute(select(ComplaintCategory).where(ComplaintCategory.code == code))).scalar_one_or_none()
        if existing is None:
            db.add(ComplaintCategory(code=code, name=code.title(), module_id=module_id, default_severity="MEDIUM"))
            await db.commit()


async def _register_and_login(client, role_hint: str = "citizen"):
    email = f"{role_hint}-{uuid.uuid4().hex[:8]}@example.com"
    await client.post("/api/v1/auth/register", json={"full_name": "Test User", "email": email, "password": "TestPass123"})
    login = await client.post("/api/v1/auth/login", json={"email": email, "password": "TestPass123"})
    return login.json()["access_token"]


@pytest.mark.asyncio
async def test_create_complaint_reported_without_ai_or_authority(client):
    await _ensure_category("TEST_ROAD_DAMAGE")
    token = await _register_and_login(client)

    resp = await client.post(
        "/api/v1/complaints",
        headers={"Authorization": f"Bearer {token}"},
        data={
            "category_code": "TEST_ROAD_DAMAGE",
            "description": "There is a large pothole outside my house causing accidents",
            "latitude": "8.71",
            "longitude": "77.72",
        },
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["category"]["code"] == "TEST_ROAD_DAMAGE"
    # AI_SERVICE_ENABLED=false in the test environment, and no authority is
    # configured for this ad-hoc category, so it should stay REPORTED.
    assert body["status"] == "REPORTED"
    assert body["assigned_authority_id"] is None


@pytest.mark.asyncio
async def test_complaint_authority_assignment_and_deadline(client):
    # Unique per run: this suite runs against a real Postgres instance, not
    # a rolled-back transaction per test, so a fixed code would collide with
    # rows left over from a previous run and pick up a stale responsibility
    # rule (both rules valid, tie-broken arbitrarily -- see assign_authority).
    category_code = f"TEST_DRAIN_BLOCKAGE_{uuid.uuid4().hex[:8]}"
    await _ensure_category(category_code, module_id="drainage")

    admin_token = await _register_and_login(client, "admin")
    # Promote to ADMIN directly via DB since role-granting requires SUPER_ADMIN.
    from app.core.security import decode_token
    from app.models.user import Role, User

    async with AsyncSessionLocal() as db:
        payload = decode_token(admin_token)
        user = (await db.execute(select(User).where(User.id == uuid.UUID(payload["sub"])))).scalar_one()
        admin_role = (await db.execute(select(Role).where(Role.name == "ADMIN"))).scalar_one()
        user.roles.append(admin_role)
        await db.commit()

    # Re-login to get a token carrying the new role claim.
    login_resp = await client.post("/api/v1/auth/login", json={"email": user.email, "password": "TestPass123"})
    admin_token = login_resp.json()["access_token"]

    boundary_resp = await client.post(
        "/api/v1/boundaries",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "Test Boundary",
            "level": "TOWN",
            "geojson": {"type": "Polygon", "coordinates": [[[77.68, 8.68], [77.76, 8.68], [77.76, 8.75], [77.68, 8.75], [77.68, 8.68]]]},
        },
    )
    assert boundary_resp.status_code == 200
    boundary_id = boundary_resp.json()["id"]

    authority_resp = await client.post(
        "/api/v1/authorities",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"name": "Test Authority", "department": "Test Dept", "level": "LOCAL_BODY", "boundary_id": boundary_id},
    )
    authority_id = authority_resp.json()["id"]

    await client.post(
        "/api/v1/authorities/responsibility-map",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"category_code": category_code, "authority_id": authority_id, "priority": 10},
    )

    citizen_token = await _register_and_login(client, "citizen")
    complaint_resp = await client.post(
        "/api/v1/complaints",
        headers={"Authorization": f"Bearer {citizen_token}"},
        data={
            "category_code": category_code,
            "description": "Blocked drain overflowing near the market",
            "latitude": "8.71",
            "longitude": "77.72",
        },
    )
    assert complaint_resp.status_code == 201
    body = complaint_resp.json()
    assert body["status"] == "ASSIGNED"
    assert body["assigned_authority_id"] == authority_id
    assert body["deadline_at"] is not None
