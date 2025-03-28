from typing import List, Optional

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas.article import ArticleCreate, ArticleUpdate
from src.db.models import Article, DeletedArticle
from src.tasks.emails import send_new_article_notification


async def create_article(
    data: ArticleCreate,
    image_url: Optional[str],
    session: AsyncSession
) -> Article:
    new_article = Article(
        title=data.title,
        content=data.content,
        category_id=data.category_id,
        image_url=image_url
    )
    session.add(new_article)
    await session.commit()
    await session.refresh(new_article)
    send_new_article_notification.delay("admin@example.com", new_article.title)
    return new_article

async def get_article_by_id(
    article_id: int,
    session: AsyncSession
) -> Optional[Article]:
    query = select(Article).where(Article.id == article_id)
    result = await session.execute(query)
    return result.scalar_one_or_none()

async def list_articles(
    session: AsyncSession,
    page_number: int = 1,
    page_size: int = 10,
    search: Optional[str] = None,
    category_id: Optional[int] = None,
) -> List[Article]:
    query = select(Article)
    if category_id:
        query = query.where(Article.category_id == category_id)
    if search:
        query = query.where(
            text("(to_tsvector('simple', coalesce(title,'')) || ' ' || coalesce(content,'')) @@ plainto_tsquery(:s)")
        ).params(s=search)

    offset = (page_number - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await session.execute(query)
    return list(result.scalars().all())

async def update_article(
    article_id: int,
    data: ArticleUpdate,
    new_image_url: Optional[str],
    session: AsyncSession
) -> Optional[Article]:
    article = await get_article_by_id(article_id, session)
    if not article:
        return None
    if data.title is not None:
        article.title = data.title  # type: ignore[assignment]
    if data.content is not None:
        article.content = data.content  # type: ignore[assignment]
    if data.category_id is not None:
        article.category_id = data.category_id  # type: ignore[assignment]
    if new_image_url is not None:
        article.image_url = new_image_url  # type: ignore[assignment]
    await session.commit()
    await session.refresh(article)
    return article

async def fake_delete_article(
    article_id: int,
    session: AsyncSession
) -> bool:
    article = await get_article_by_id(article_id, session)
    if not article:
        return False

    deleted_art = DeletedArticle(
        id=article.id,
        title=article.title,
        content=article.content,
        image_url=article.image_url,
        category_id=article.category_id,
    )
    session.add(deleted_art)
    await session.delete(article)
    await session.commit()
    return True
