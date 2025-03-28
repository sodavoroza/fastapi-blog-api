from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas.category import CategoryCreate, CategoryRead
from src.db.models import Category


async def create_category(
    data: CategoryCreate,
    session: AsyncSession,
) -> Category:
    new_cat = Category(name=data.name)
    session.add(new_cat)
    await session.commit()
    await session.refresh(new_cat)
    return new_cat

async def list_categories(
    session: AsyncSession,
    page_number: int = 1,
    page_size: int = 10,
) -> List[CategoryRead]:
    offset = (page_number - 1) * page_size
    query = select(Category).offset(offset).limit(page_size)
    result = await session.execute(query)
    categories = result.scalars().all()
    return [CategoryRead.model_validate(category) for category in categories]
