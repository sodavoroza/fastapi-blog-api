import os
import socket
import time
from typing import AsyncGenerator, Generator

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from src.db.session import get_async_session
from src.main import app

# Отключаем вызовы Celery-задач (чтобы тесты не пытались подключиться к брокеру)
from src.tasks.emails import send_welcome_email, send_new_article_notification
send_welcome_email.delay = lambda *args, **kwargs: None
send_new_article_notification.delay = lambda *args, **kwargs: None

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://postgres:password@localhost:5432/blog_test",
)

def wait_for_db(host: str, port: int, timeout: int = 30) -> None:
    start = time.time()
    while True:
        try:
            socket.getaddrinfo(host, port)
            return
        except socket.gaierror:
            if time.time() - start > timeout:
                raise
            time.sleep(1)

# Ждем, пока база станет доступной (для локального тестирования)
wait_for_db("localhost", 5432)

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
