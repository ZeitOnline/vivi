"""add additional volume columns

Revision ID: 7befcb5fd162
Revises: 2f7a8b0212ae
Create Date: 2025-04-09 14:38:10.391543

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7befcb5fd162'
down_revision: Union[str, None] = '2f7a8b0212ae'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'properties',
        sa.Column('volume_date_digital_published', sa.TIMESTAMP(timezone=True), nullable=True),
    )
    op.add_column('properties', sa.Column('volume_note', sa.Unicode(), nullable=True))


def downgrade() -> None:
    op.drop_column('properties', 'volume_note')
    op.drop_column('properties', 'volume_date_digital_published')
