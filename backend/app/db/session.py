from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import settings

# pytest-asyncio gives each test function its own event loop. A pooled
# connection acquired under one loop can't be reused under another ("Task
# ... attached to a different loop"), so tests run with NullPool -- every
# checkout is a fresh connection, which sidesteps the whole class of error.
# Production keeps normal pooling (pool_pre_ping) for performance.
_engine_kwargs = {"echo": False, "future": True}
if settings.TESTING:
    _engine_kwargs["poolclass"] = NullPool
else:
    _engine_kwargs["pool_pre_ping"] = True

engine = create_async_engine(settings.DATABASE_URL, **_engine_kwargs)

AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
