from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies.auth import get_current_user
from src.api.schemas.article import ArticleCreate, ArticleRead, ArticleUpdate
from src.db.models import User
from src.db.session import get_async_session
from src.services.article_service import (
    create_article,
    fake_delete_article,
    get_article_by_id,
    list_articles,
    update_article,
)
from src.services.s3_service import upload_image_to_s3

router = APIRouter(prefix="/articles", tags=["Articles"])

@router.post("/", response_model=ArticleRead)
async def create_new_article(
    title: str = Form(...),
    content: str = Form(...),
    category_id: Optional[int] = Form(None),
    image: Optional[UploadFile] = File(None),
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> ArticleRead:
    image_url = None
    if image:
        file_bytes = await image.read()
        image_url = upload_image_to_s3(file_bytes, str(image.filename))
    article_data = ArticleCreate(title=title, content=content, category_id=category_id)
    new_article = await create_article(article_data, image_url, session)
    return ArticleRead.model_validate(new_article)

@router.get("/", response_model=List[ArticleRead])
async def read_articles(
    page_number: int = 1,
    page_size: int = 10,
    search: Optional[str] = None,
    category_id: Optional[int] = None,
    session: AsyncSession = Depends(get_async_session),
) -> List[ArticleRead]:
    articles = await list_articles(session, page_number, page_size, search, category_id)
    return [ArticleRead.model_validate(article) for article in articles]

@router.get("/{article_id}", response_model=ArticleRead)
async def get_article(
    article_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> ArticleRead:
    article = await get_article_by_id(article_id, session)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return ArticleRead.model_validate(article)

@router.put("/{article_id}", response_model=ArticleRead)
async def update_existing_article(
    article_id: int,
    title: Optional[str] = Form(None),
    content: Optional[str] = Form(None),
    category_id: Optional[int] = Form(None),
    image: Optional[UploadFile] = File(None),
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> ArticleRead:
    article = await get_article_by_id(article_id, session)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    new_image_url = None
    if image is not None:
        file_bytes = await image.read()
        new_image_url = upload_image_to_s3(file_bytes, str(image.filename))
    updated_article = await update_article(
        article_id,
        ArticleUpdate(title=title, content=content, category_id=category_id),
        new_image_url,
        session
    )
    if not updated_article:
        raise HTTPException(status_code=404, detail="Article not found")
    return ArticleRead.model_validate(updated_article)

@router.delete("/{article_id}")
async def delete_article(
    article_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    success = await fake_delete_article(article_id, session)
    if not success:
        raise HTTPException(status_code=404, detail="Article not found")
    return {"message": "Article fake-deleted successfully"}
