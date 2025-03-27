"""add_deleted_articles_title_index

Revision ID: 63cec843bac0
Revises: 826aa0e40078
Create Date: 2025-03-25 19:52:29.891457

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '63cec843bac0'
down_revision: Union[str, None] = '826aa0e40078'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    with op.batch_alter_table("deleted_articles") as batch_op:
        batch_op.create_index("ix_deleted_articles_title", ["title"])



def downgrade() -> None:
    """Downgrade schema."""
    pass
