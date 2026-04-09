import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from httpx import ASGITransport, AsyncClient

from news_radar.database import Base, get_db
from news_radar.main import app

# In-memory SQLite for test isolation
test_engine = create_async_engine("sqlite+aiosqlite://", echo=True)
test_session_factory = async_sessionmaker(test_engine, expire_on_commit=False)


async def _override_get_db():
    async with test_session_factory() as session:
        yield session


app.dependency_overrides[get_db] = _override_get_db


@pytest.fixture(autouse=True)
async def _setup_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
