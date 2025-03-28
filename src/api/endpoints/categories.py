from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies.auth import get_current_user
from src.api.schemas.category import CategoryCreate, CategoryRead
from src.db.models import User
from src.db.session import get_async_session
from src.services.category_service import create_category, list_categories

router = APIRouter(prefix="/categories", tags=["Categories"])

@router.get("/", response_model=List[CategoryRead])
async def read_categories(
    page_number: int = 1,
    page_size: int = 10,
    session: AsyncSession = Depends(get_async_session)
) -> List[CategoryRead]:
    return await list_categories(session, page_number, page_size)

@router.post("/", response_model=CategoryRead)
async def create_new_category(
    data: CategoryCreate,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> CategoryRead:
    if not current_user.is_active:
        raise HTTPException(status_code=403, detail="Inactive user cannot create categories")
    new_cat = await create_category(data, session)
    return CategoryRead.model_validate(new_cat)
