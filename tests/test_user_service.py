import pytest
from src.db.models import User
from src.services.user_service import authenticate_user, create_user
from src.api.schemas.user import UserCreate
from fastapi import HTTPException
from src.core.security import get_password_hash

@pytest.mark.asyncio
async def test_authenticate_user_wrong_password(override_db_dependency, test_session):
    async with test_session as session:
        # Генерируем корректный хеш для пароля "correctpass"
        valid_hash = get_password_hash("correctpass")
        user = User(email="found@example.com", hashed_password=valid_hash, is_active=True)
        session.add(user)
        await session.commit()
        # Попытка аутентификации с неверным паролем должна вернуть None
        result = await authenticate_user("found@example.com", "wrongpass", session)
        assert result is None

@pytest.mark.asyncio
async def test_create_user_ok(override_db_dependency, test_session, mocker):
    mock_send = mocker.patch("src.services.user_service.send_welcome_email.delay")
    async with test_session as session:
        new_user = await create_user(UserCreate(email="direct@example.com", password="mypwd"), session)
        assert new_user.id is not None
        assert new_user.email == "direct@example.com"
        mock_send.assert_called_once_with("direct@example.com")

@pytest.mark.asyncio
async def test_create_user_duplicate(override_db_dependency, test_session):
    async with test_session as session:
        user = User(email="dupe@example.com", hashed_password="xx", is_active=True)
        session.add(user)
        await session.commit()
        with pytest.raises(HTTPException) as exc:
            await create_user(UserCreate(email="dupe@example.com", password="any"), session)
        assert exc.value.status_code == 400
        assert "already exists" in exc.value.detail
