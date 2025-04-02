"""add audio_type column

Revision ID: ef06d4a56605
Revises: ee9a6b65f816
Create Date: 2025-03-31 13:28:27.626620

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ef06d4a56605'
down_revision: Union[str, None] = 'ee9a6b65f816'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('properties', sa.Column('audio_type', sa.Unicode(), nullable=True))


def downgrade() -> None:
    op.drop_column('properties', 'audio_type')
