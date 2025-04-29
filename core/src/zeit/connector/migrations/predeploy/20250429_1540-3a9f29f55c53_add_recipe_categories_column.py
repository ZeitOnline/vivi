"""add recipe_categories column

Revision ID: 3a9f29f55c53
Revises: 7befcb5fd162
Create Date: 2025-04-29 15:40:39.792125

"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy.dialects.postgresql import JSONB
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3a9f29f55c53'
down_revision: Union[str, None] = '7befcb5fd162'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('properties', sa.Column('recipe_categories', JSONB(), nullable=True))


def downgrade() -> None:
    op.drop_column('properties', 'recipe_categories')
