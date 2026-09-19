import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.main import app
from app.models.enums import RoleName
from app.models.user import Role


@pytest_asyncio.fixture(autouse=True)
async def seed_roles():
    # Function-scoped (not session-scoped): the async engine's connection
    # pool binds to the event loop of the test that first used it, and
    # pytest-asyncio (asyncio_mode=auto) creates a fresh loop per test --
    # a session-scoped fixture/engine use would outlive that loop and fail
    # with "attached to a different loop".
    async with AsyncSessionLocal() as db:
        existing = {r.name for r in (await db.execute(select(Role))).scalars().all()}
        for role in RoleName:
            if role.value not in existing:
                db.add(Role(name=role.value))
        await db.commit()


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
