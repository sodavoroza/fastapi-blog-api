import pytest
from httpx import AsyncClient
from src.main import app

@pytest.mark.asyncio
async def test_register_success(override_db_dependency):
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        resp = await ac.post("/auth/register", json={"email": "user@example.com", "password": "testpass"})
        assert resp.status_code == 200
        data = resp.json()
        assert "id" in data
        assert data["email"] == "user@example.com"

@pytest.mark.asyncio
async def test_register_duplicate_email(override_db_dependency):
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        resp1 = await ac.post("/auth/register", json={"email": "dupe@example.com", "password": "12345"})
        assert resp1.status_code == 200
        resp2 = await ac.post("/auth/register", json={"email": "dupe@example.com", "password": "99999"})
        assert resp2.status_code == 400
        assert "already exists" in resp2.text

@pytest.mark.asyncio
async def test_login_success(override_db_dependency):
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        await ac.post("/auth/register", json={"email": "login@example.com", "password": "pass123"})
        resp = await ac.post("/auth/login", json={"email": "login@example.com", "password": "pass123"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["message"] == "Login successful"
        assert "access_token" in data

@pytest.mark.asyncio
async def test_login_wrong_password(override_db_dependency):
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        await ac.post("/auth/register", json={"email": "wrong@example.com", "password": "realpass"})
        resp = await ac.post("/auth/login", json={"email": "wrong@example.com", "password": "fakepass"})
        assert resp.status_code == 400
        assert "Invalid credentials" in resp.text

@pytest.mark.asyncio
async def test_auth_wrong_scheme(override_db_dependency):
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        resp = await ac.get("/protected/me", headers={"Authorization": "Basic abcd"})
        assert resp.status_code == 401
        assert "Not authenticated" in resp.text

@pytest.mark.asyncio
async def test_auth_invalid_payload_no_sub(override_db_dependency, mocker):
    mock_decode = mocker.patch("src.api.dependencies.auth.jwt.decode")
    mock_decode.return_value = {}
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        resp = await ac.get("/protected/me", headers={"Authorization": "Bearer abc"})
        assert resp.status_code == 401
        assert "Invalid token" in resp.text

@pytest.mark.asyncio
async def test_auth_jwt_error(override_db_dependency, mocker):
    from jose import JWTError
    mocker.patch("src.api.dependencies.auth.jwt.decode", side_effect=JWTError("Signature invalid"))
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        resp = await ac.get("/protected/me", headers={"Authorization": "Bearer abc"})
        assert resp.status_code == 401
        assert "Invalid token" in resp.text
