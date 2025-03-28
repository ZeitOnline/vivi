"""add column date_last_retracted

Revision ID: ee9a6b65f816
Revises: 8a302c7ec38c
Create Date: 2025-03-28 11:20:25.690833

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ee9a6b65f816'
down_revision: Union[str, None] = '8a302c7ec38c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'properties', sa.Column('date_last_retracted', sa.TIMESTAMP(timezone=True), nullable=True)
    )


def downgrade() -> None:
    op.drop_column('properties', 'date_last_retracted')
