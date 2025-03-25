"""Add article_template column

Revision ID: 8a302c7ec38c
Revises: 2a5901312f94
Create Date: 2025-03-25 15:36:41.880057

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8a302c7ec38c'
down_revision: Union[str, None] = '2a5901312f94'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('properties', sa.Column('article_template', sa.Unicode(), nullable=True))


def downgrade() -> None:
    op.drop_column('properties', 'article_template')
