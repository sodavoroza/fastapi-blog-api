from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

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


    op.create_index(
        op.f("ix_deleted_articles_id"), "deleted_articles", ["id"], unique=False
    )


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

    op.execute("DROP INDEX IF EXISTS idx_articles_fts;")
    op.drop_table("articles")
    op.drop_table("deleted_articles")
