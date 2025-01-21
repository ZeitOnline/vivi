"""add video_type column

Revision ID: f7f17b16292c
Revises: 0d681d9ffda0
Create Date: 2025-01-20 11:06:16.852051

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f7f17b16292c'
down_revision: Union[str, None] = '0d681d9ffda0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('properties', sa.Column('video_type', sa.Unicode(), nullable=True))


def downgrade() -> None:
    op.drop_column('properties', 'video_type')
