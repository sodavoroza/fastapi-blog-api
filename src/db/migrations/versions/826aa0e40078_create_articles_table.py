"""create_articles_table

Revision ID: 826aa0e40078
Revises: 98088e19dca4
Create Date: 2025-03-25 12:46:58.335017
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "826aa0e40078"
down_revision: Union[str, None] = "98088e19dca4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Upgrade schema.
    Creates:
      - deleted_articles (with full columns)
      - articles
      - indexes on articles
      - a GIN FTS index on articles for (title + content)
    """

    # Создаём таблицу deleted_articles (для fake delete),
    # указываем столбцы явно, в т.ч. title, content, image_url...
    op.create_table(
        "deleted_articles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("image_url", sa.String(), nullable=True),
        sa.Column("category_id", sa.Integer(), nullable=True),
        sa.Column(
            "deleted_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Индекс по id (нормально). Если хотите индекс по title —
    # вынесли в новую миграцию, значит здесь закомментируем.
    op.create_index(
        op.f("ix_deleted_articles_id"), "deleted_articles", ["id"], unique=False
    )
    # op.create_index(
    #     op.f("ix_deleted_articles_title"),
    #     "deleted_articles",
    #     ["title"],
    #     unique=False,
    # )

    # Создаём таблицу articles
    op.create_table(
        "articles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("image_url", sa.String(), nullable=True),
        sa.Column("category_id", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_articles_id"), "articles", ["id"], unique=False)
    op.create_index(op.f("ix_articles_title"), "articles", ["title"], unique=False)

    # Создаём GIN-индекс для полнотекстового поиска
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_articles_fts
        ON articles
        USING GIN (
          to_tsvector('simple', coalesce(title,'') || ' ' || coalesce(content,''))
        );
        """
    )


def downgrade() -> None:
    """
    Downgrade schema.
    """

    # Если хотите полноценное удаление:
    op.execute("DROP INDEX IF EXISTS idx_articles_fts;")
    op.drop_table("articles")
    op.drop_table("deleted_articles")

    # Прочие автосгенерированные операции можно добавить,
    # если Alembic что-то генерировал автоматом.
