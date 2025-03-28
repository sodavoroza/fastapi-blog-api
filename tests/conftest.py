import os
import socket
import time
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from src.db.session import get_async_session
from src.main import app

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://postgres:password@localhost:5432/blog_test",
)
TEST_DATABASE_HOST = os.getenv("TEST_DATABASE_HOST", "localhost")

def wait_for_db(host: str, port: int, timeout: int = 30) -> None:
    start = time.time()
    while True:
        try:
            socket.getaddrinfo(host, port)
            return
        except socket.gaierror:
            if time.time() - start > timeout:
                raise Exception(f"Database {host}:{port} is not available")
            time.sleep(1)

wait_for_db(TEST_DATABASE_HOST, 5432)

@pytest.fixture(scope="function", autouse=True)
async def run_truncate_tables():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.execute(text('TRUNCATE "users" RESTART IDENTITY CASCADE'))
        await conn.execute(text('TRUNCATE "articles" RESTART IDENTITY CASCADE'))
        await conn.execute(text('TRUNCATE "deleted_articles" RESTART IDENTITY CASCADE'))
        await conn.execute(text('TRUNCATE "categories" RESTART IDENTITY CASCADE'))
    await engine.dispose()

@pytest.fixture
async def test_session():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    AsyncTestSession = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with AsyncTestSession() as session:
        yield session
    await engine.dispose()

async def override_get_async_session():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    AsyncTestSession = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with AsyncTestSession() as session:
        yield session
    await engine.dispose()

@pytest.fixture
def override_db_dependency():
    app.dependency_overrides[get_async_session] = override_get_async_session
    yield
    app.dependency_overrides.clear()
