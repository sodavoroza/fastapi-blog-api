import pytest
from uuid import uuid4
from src.db.models import Article, Category
from src.api.schemas.article import ArticleUpdate
from src.services.article_service import update_article, list_articles, fake_delete_article



@pytest.mark.asyncio
async def test_update_article_ok(override_db_dependency, test_session):
    async with test_session as session:
        cat1 = Category(name="CatOne")
        cat2 = Category(name="CatTwo")
        session.add_all([cat1, cat2])
        await session.commit()
        await session.refresh(cat1)
        await session.refresh(cat2)

        art = Article(title="OldTitle", content="OldContent", category_id=cat1.id)
        session.add(art)
        await session.commit()
        await session.refresh(art)

        updated = await update_article(
            article_id=art.id,
            data=ArticleUpdate(title="NewTitle", content="NewContent", category_id=cat2.id),
            new_image_url="http://example.com/img.jpg",
            session=session,
        )
        assert updated is not None
        assert updated.title == "NewTitle"
        assert updated.content == "NewContent"
        assert updated.category_id == cat2.id
        assert updated.image_url == "http://example.com/img.jpg"

@pytest.mark.asyncio
async def test_update_article_not_found(override_db_dependency, test_session):
    async with test_session as session:
        updated = await update_article(
            article_id=999999,
            data=ArticleUpdate(title="???"),
            new_image_url=None,
            session=session,
        )
        assert updated is None

@pytest.mark.asyncio
async def test_fake_delete_article_not_found(override_db_dependency, test_session):
    async with test_session as session:
        result = await fake_delete_article(article_id=999999, session=session)
        assert result is False

@pytest.mark.asyncio
async def test_list_articles_search(override_db_dependency, test_session):
    async with test_session as session:
        cat = Category(name=f"SearchCat_{uuid4()}")
        session.add(cat)
        await session.commit()
        await session.refresh(cat)

        session.add_all([
            Article(title="UniqueTitle123", content="Content1", category_id=cat.id),
            Article(title="AnotherTitle", content="Content2", category_id=cat.id),
        ])
        await session.commit()

        articles = await list_articles(search="UniqueTitle123", session=session)
        assert len(articles) == 1
        assert articles[0].title == "UniqueTitle123"
