import os
import socket
import time
from collections.abc import AsyncGenerator, Generator

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.db.session import get_async_session
from src.main import app
from src.tasks.emails import send_new_article_notification, send_welcome_email


@pytest.fixture(autouse=True)
def override_celery_tasks(monkeypatch):
    monkeypatch.setattr(send_welcome_email, "delay", lambda *args, **kwargs: None)
    monkeypatch.setattr(send_new_article_notification, "delay", lambda *args, **kwargs: None)

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://postgres:password@localhost:5432/blog_test",
)

def wait_for_db(host: str, port: int, timeout: int = 60) -> None:
    start = time.time()
    while True:
        try:
            socket.getaddrinfo(host, port)
            break
        except socket.gaierror:
            if time.time() - start > timeout:
                raise Exception(f"Database {host}:{port} is not available")
            time.sleep(1)

wait_for_db(os.getenv("POSTGRES_HOST", "localhost"), 5432)

@pytest.fixture(scope="function", autouse=True)
async def run_truncate_tables() -> None:
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        try:
            await conn.execute(text('TRUNCATE "users" RESTART IDENTITY CASCADE'))
        except Exception:
            pass
        try:
            await conn.execute(text('TRUNCATE "articles" RESTART IDENTITY CASCADE'))
        except Exception:
            pass
        try:
            await conn.execute(text('TRUNCATE "deleted_articles" RESTART IDENTITY CASCADE'))
        except Exception:
            pass
        try:
            await conn.execute(text('TRUNCATE "categories" RESTART IDENTITY CASCADE'))
        except Exception:
            pass
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
