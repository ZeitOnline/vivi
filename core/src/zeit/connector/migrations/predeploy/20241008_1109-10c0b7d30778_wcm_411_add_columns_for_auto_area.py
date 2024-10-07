"""wcm_411_add_columns_for_auto_area

Revision ID: 10c0b7d30778
Revises: 28355ecfa735
Create Date: 2024-10-08 11:09:56.473460

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '10c0b7d30778'
down_revision: Union[str, None] = '28355ecfa735'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('properties', sa.Column('access', sa.Unicode(), nullable=True))
    op.add_column('properties', sa.Column('product', sa.Unicode(), nullable=True))
    op.add_column('properties', sa.Column('ressort', sa.Unicode(), nullable=True))
    op.add_column('properties', sa.Column('sub_ressort', sa.Unicode(), nullable=True))
    op.add_column('properties', sa.Column('series', sa.Unicode(), nullable=True))
    op.add_column('properties', sa.Column('print_ressort', sa.Unicode(), nullable=True))
    op.add_column('properties', sa.Column('volume_year', sa.Integer(), nullable=True))
    op.add_column('properties', sa.Column('volume_number', sa.Integer(), nullable=True))
    op.add_column(
        'properties', sa.Column('published', sa.Boolean(), server_default='false', nullable=True)
    )
    op.add_column('properties', sa.Column('article_genre', sa.Unicode(), nullable=True))


def downgrade() -> None:
    op.drop_column('properties', 'article_genre')
    op.drop_column('properties', 'published')
    op.drop_column('properties', 'volume_number')
    op.drop_column('properties', 'volume_year')
    op.drop_column('properties', 'print_ressort')
    op.drop_column('properties', 'series')
    op.drop_column('properties', 'sub_ressort')
    op.drop_column('properties', 'ressort')
    op.drop_column('properties', 'product')
    op.drop_column('properties', 'access')
