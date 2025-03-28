import pytest
from httpx import AsyncClient

from src.main import app


@pytest.mark.asyncio
async def test_create_article(override_db_dependency):
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        await ac.post("/auth/register", json={"email": "article@example.com", "password": "pass123"})
        login_resp = await ac.post("/auth/login", json={"email": "article@example.com", "password": "pass123"})
        token = login_resp.json()["access_token"]

        headers = {"Authorization": f"Bearer {token}"}
        resp = await ac.post("/articles/", headers=headers, data={"title": "Test", "content": "Hello"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["title"] == "Test"

@pytest.mark.asyncio
async def test_get_article_by_id(override_db_dependency):
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        await ac.post("/auth/register", json={"email": "oneart@example.com", "password": "pass123"})
        login_resp = await ac.post("/auth/login", json={"email": "oneart@example.com", "password": "pass123"})
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        resp_art = await ac.post("/articles/", headers=headers, data={"title": "OneArt", "content": "Abc"})
        art_id = resp_art.json()["id"]
        get_resp = await ac.get(f"/articles/{art_id}")
        assert get_resp.status_code == 200
        art_data = get_resp.json()
        assert art_data["title"] == "OneArt"
        assert art_data["id"] == art_id

@pytest.mark.asyncio
async def test_list_articles(override_db_dependency):
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        await ac.post("/auth/register", json={"email": "listart@example.com", "password": "pass123"})
        login_resp = await ac.post("/auth/login", json={"email": "listart@example.com", "password": "pass123"})
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        await ac.post("/articles/", headers=headers, data={"title": "Art1", "content": "C1"})
        await ac.post("/articles/", headers=headers, data={"title": "Art2", "content": "C2"})

        list_resp = await ac.get("/articles/", headers=headers)
        assert list_resp.status_code == 200
        articles = list_resp.json()
        assert len(articles) == 2
        titles = [a["title"] for a in articles]
        assert "Art1" in titles
        assert "Art2" in titles

@pytest.mark.asyncio
async def test_fake_delete_article(override_db_dependency):
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        await ac.post("/auth/register", json={"email": "fdelete@example.com", "password": "pass123"})
        login_resp = await ac.post("/auth/login", json={"email": "fdelete@example.com", "password": "pass123"})
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        resp_art = await ac.post("/articles/", headers=headers, data={"title": "DeleteMe", "content": "DD"})
        art_id = resp_art.json()["id"]

        del_resp = await ac.delete(f"/articles/{art_id}", headers=headers)
        assert del_resp.status_code == 200
        msg = del_resp.json()["message"]
        assert "fake-deleted" in msg

        get_resp = await ac.get(f"/articles/{art_id}")
        assert get_resp.status_code == 404
        assert "not found" in get_resp.text
