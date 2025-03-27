from fastapi import Depends, Request, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.db.models import User
from src.db.session import get_async_session
from src.core.security import SECRET_KEY, ALGORITHM

http_bearer = HTTPBearer(auto_error=False)

async def get_current_user(
    request: Request,
    session: AsyncSession = Depends(get_async_session),
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer)
) -> User:
    token = None

    cookie_token = request.cookies.get("access_token")
    if cookie_token:
        token = cookie_token

    if not token and credentials and credentials.scheme == "Bearer":
        token = credentials.credentials

    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")  # <-- 401

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")  # type: ignore
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    result = await session.execute(
        select(User).where(User.email == email)
    )
    user_obj = result.scalar_one_or_none()

    if user_obj is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user_obj
