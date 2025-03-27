from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas.user import UserCreate, UserLogin, UserRead
from src.core.security import create_access_token
from src.db.session import get_async_session
from src.services.user_service import authenticate_user, create_user

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register")
async def register(
    user: UserCreate,
    session: AsyncSession = Depends(get_async_session),
) -> UserRead:
    new_user = await create_user(user, session)
    return UserRead.model_validate(new_user)

@router.post("/login")
async def login(
    user: UserLogin,
    session: AsyncSession = Depends(get_async_session),
) -> JSONResponse:
    db_user = await authenticate_user(user.email, user.password, session)
    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": db_user.email})
    response_data = {
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "bearer",
    }
    response = JSONResponse(content=response_data)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=60 * 30,
        secure=True,
        samesite="lax",
    )
    return response
