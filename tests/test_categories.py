import pytest
from httpx import AsyncClient
from src.main import app

@pytest.mark.asyncio
async def test_create_category(override_db_dependency):
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        await ac.post("/auth/register", json={"email": "cat@example.com", "password": "catpass"})
        login_resp = await ac.post("/auth/login", json={"email": "cat@example.com", "password": "catpass"})
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        resp = await ac.post("/categories/", headers=headers, json={"name": "Python"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "Python"

@pytest.mark.asyncio
async def test_list_categories(override_db_dependency):
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        await ac.post("/auth/register", json={"email": "catlist@example.com", "password": "catpass"})
        login_resp = await ac.post("/auth/login", json={"email": "catlist@example.com", "password": "catpass"})
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        await ac.post("/categories/", headers=headers, json={"name": "Music"})
        await ac.post("/categories/", headers=headers, json={"name": "News"})
        list_resp = await ac.get("/categories/", headers=headers)
        assert list_resp.status_code == 200
        cats = list_resp.json()
        assert len(cats) == 2
        cat_names = [c["name"] for c in cats]
        assert "Music" in cat_names
        assert "News" in cat_names
