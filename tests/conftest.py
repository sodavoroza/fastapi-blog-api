import os
import time
import socket
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from collections.abc import AsyncGenerator, Generator
from src.db.session import get_async_session
from src.main import app

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://postgres:password@db:5432/blog_test",
)

def wait_for_db(host: str, port: int, timeout: int = 10) -> None:
    host = os.getenv("TEST_DATABASE_HOST", host)
    start = time.time()
    while time.time() - start < timeout:
        try:
            socket.getaddrinfo(host, port)
            return
        except socket.gaierror:
            time.sleep(0.5)
    raise Exception(f"Database {host}:{port} is not available")

wait_for_db("db", 5432)

@pytest.fixture(autouse=True)
async def run_truncate_tables() -> None:
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.execute(text('TRUNCATE "users" RESTART IDENTITY CASCADE'))
        await conn.execute(text('TRUNCATE "articles" RESTART IDENTITY CASCADE'))
        await conn.execute(text('TRUNCATE "deleted_articles" RESTART IDENTITY CASCADE'))
        await conn.execute(text('TRUNCATE "categories" RESTART IDENTITY CASCADE'))
    await engine.dispose()

@pytest.fixture
async def test_session() -> AsyncGenerator[AsyncSession, None]:
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    AsyncTestSession = async_sessionmaker(engine, expire_on_commit=False)
    async with AsyncTestSession() as session:
        yield session
    await engine.dispose()

async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    AsyncTestSession = async_sessionmaker(engine, expire_on_commit=False)
    async with AsyncTestSession() as session:
        yield session
    await engine.dispose()

@pytest.fixture
def override_db_dependency() -> Generator[None, None, None]:
    app.dependency_overrides[get_async_session] = override_get_async_session
    yield
    app.dependency_overrides.clear()
