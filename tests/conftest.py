import os
import socket
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from src.db.models import Base  # убедитесь, что Base импортируется из вашего модуля моделей
from src.db.session import get_async_session
from src.main import app

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://postgres:password@db:5432/blog_test",
)

# Фикстура, которая создаёт таблицы и очищает их перед каждым тестом.
@pytest.fixture(scope="function", autouse=True)
async def run_truncate_tables():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        # Создаем таблицы, если их еще нет
        await conn.run_sync(Base.metadata.create_all)
        # Затем очищаем таблицы
        await conn.execute(text('TRUNCATE "users" RESTART IDENTITY CASCADE'))
        await conn.execute(text('TRUNCATE "articles" RESTART IDENTITY CASCADE'))
        await conn.execute(text('TRUNCATE "deleted_articles" RESTART IDENTITY CASCADE'))
        await conn.execute(text('TRUNCATE "categories" RESTART IDENTITY CASCADE'))
    await engine.dispose()


# Фикстура для получения тестовой сессии.
@pytest.fixture
async def test_session():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session() as session:
        yield session
    await engine.dispose()


# Переопределяем зависимость get_async_session в приложении для тестирования.
async def override_get_async_session():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session() as session:
        yield session
    await engine.dispose()


@pytest.fixture
def override_db_dependency():
    app.dependency_overrides[get_async_session] = override_get_async_session
    yield
    app.dependency_overrides.clear()


def wait_for_db(host: str, port: int, timeout: int = 10) -> None:
    import time

    host = os.getenv("TEST_DATABASE_HOST", host)
    start = time.time()
    while time.time() - start < timeout:
        try:
            socket.getaddrinfo(host, port)
            return
        except socket.gaierror:
            time.sleep(0.5)
    raise Exception(f"Database {host}:{port} is not available")

    

# Если требуется дождаться доступности БД перед тестами, можно вызвать wait_for_db() здесь.
wait_for_db("db", 5432)
