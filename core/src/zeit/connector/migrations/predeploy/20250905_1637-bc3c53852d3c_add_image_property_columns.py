"""Add image property columns

Revision ID: bc3c53852d3c
Revises: 3728b49cfd36
Create Date: 2025-09-05 16:37:21.816074

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bc3c53852d3c'
down_revision: Union[str, None] = '3728b49cfd36'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('properties', sa.Column('image_mime_type', sa.Unicode(), nullable=True))
    op.add_column('properties', sa.Column('image_height', sa.Integer(), nullable=True))
    op.add_column('properties', sa.Column('image_width', sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column('properties', 'image_width')
    op.drop_column('properties', 'image_height')
    op.drop_column('properties', 'image_mime_type')
