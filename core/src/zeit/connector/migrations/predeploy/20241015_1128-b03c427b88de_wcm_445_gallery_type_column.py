"""WCM-445_gallery_type_column

Revision ID: b03c427b88de
Revises: 10c0b7d30778
Create Date: 2024-10-15 11:28:23.231396

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b03c427b88de'
down_revision: Union[str, None] = '10c0b7d30778'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('properties', sa.Column('gallery_type', sa.Unicode(), nullable=True))


def downgrade() -> None:
    op.drop_column('properties', 'gallery_type')
