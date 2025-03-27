import pytest
from httpx import AsyncClient
from src.main import app

@pytest.mark.asyncio
async def test_users_test_endpoint(override_db_dependency):
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        resp = await ac.get("/users/test")
        assert resp.status_code == 200
        assert resp.json() == {"msg": "Users endpoint is working!"}
