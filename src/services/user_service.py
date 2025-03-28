from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.api.schemas.user import UserCreate
from src.core.security import get_password_hash, verify_password
from src.db.models import User
from src.tasks.emails import send_welcome_email


async def authenticate_user(
    email: str,
    password: str,
    session: AsyncSession,
) -> User | None:
    query = select(User).where(User.email == email)
    result = await session.execute(query)
    user = result.scalar_one_or_none()
    if not user or not verify_password(password, str(user.hashed_password)):
        return None
    return user

async def create_user(user_create: UserCreate, session: AsyncSession) -> User:
    query = select(User).where(User.email == user_create.email)
    result = await session.execute(query)
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=400, detail="User with this email already exists"
        )
    hashed_password = get_password_hash(user_create.password)
    db_user = User(
        email=user_create.email,
        hashed_password=hashed_password,
        is_active=True,
    )
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    send_welcome_email.delay(db_user.email)
    return db_user
