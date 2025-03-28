import pytest
from httpx import AsyncClient

from src.main import app


@pytest.mark.asyncio
async def test_me_unauthorized(override_db_dependency):
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        resp = await ac.get("/protected/me")
        assert resp.status_code == 401
        assert "Not authenticated" in resp.text

@pytest.mark.asyncio
async def test_me_ok(override_db_dependency):
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        await ac.post("/auth/register", json={"email": "me@example.com", "password": "pass123"})
        login_resp = await ac.post("/auth/login", json={"email": "me@example.com", "password": "pass123"})
        token = login_resp.json()["access_token"]
        resp = await ac.get("/protected/me", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == "me@example.com"
