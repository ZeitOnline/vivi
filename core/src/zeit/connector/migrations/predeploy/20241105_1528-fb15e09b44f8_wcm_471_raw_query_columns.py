"""WCM-471: raw query columns

Revision ID: fb15e09b44f8
Revises: b03c427b88de
Create Date: 2024-11-05 15:28:03.522675

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fb15e09b44f8'
down_revision: Union[str, None] = 'b03c427b88de'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('properties', sa.Column('print_page', sa.Integer(), nullable=True))
    op.add_column(
        'properties', sa.Column('article_audio_premium_enabled', sa.Boolean(), nullable=True)
    )
    op.add_column(
        'properties', sa.Column('article_audio_speech_enabled', sa.Boolean(), nullable=True)
    )
    op.add_column('properties', sa.Column('article_header', sa.Unicode(), nullable=True))
    op.add_column('properties', sa.Column('centerpage_type', sa.Unicode(), nullable=True))
    op.add_column('properties', sa.Column('seo_meta_robots', sa.Unicode(), nullable=True))


def downgrade() -> None:
    op.drop_column('properties', 'seo_meta_robots')
    op.drop_column('properties', 'centerpage_type')
    op.drop_column('properties', 'article_header')
    op.drop_column('properties', 'article_audio_speech_enabled')
    op.drop_column('properties', 'article_audio_premium_enabled')
    op.drop_column('properties', 'print_page')
