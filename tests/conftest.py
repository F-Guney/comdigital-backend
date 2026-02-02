import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import get_db
from app.models.base import Base
from app.main import app

TEST_DATABASE_URL = "postgresql+asyncpg://comdigital:comdigital@localhost:5432/comdigital_test"


@pytest_asyncio.fixture(autouse=True)
async def db_setup():
    """Fresh engine per test — same event loop, no asyncpg conflicts."""
    engine = create_async_engine(TEST_DATABASE_URL)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False
    )

    async def override_get_db():
        async with factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = override_get_db
    yield

    async with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())

    app.dependency_overrides.clear()
    await engine.dispose()


@pytest_asyncio.fixture
async def client() -> AsyncClient:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def auth_headers(client: AsyncClient) -> dict:
    await client.post(
        "/api/users/register",
        json={
            "email": "fixture@example.com",
            "password": "testpass123",
            "first_name": "Test",
            "last_name": "User",
        },
    )
    resp = await client.post(
        "/api/users/login",
        json={"email": "fixture@example.com", "password": "testpass123"},
    )
    token = resp.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}
