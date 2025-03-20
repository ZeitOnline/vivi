"""add scheduled publish/retract columns

Revision ID: 2a5901312f94
Revises: 2df03d84be31
Create Date: 2025-03-17 15:55:57.510505

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2a5901312f94'
down_revision: Union[str, None] = '2df03d84be31'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'properties',
        sa.Column('date_scheduled_publish', sa.TIMESTAMP(timezone=True), nullable=True),
    )
    op.add_column(
        'properties',
        sa.Column('date_scheduled_retract', sa.TIMESTAMP(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column('properties', 'date_scheduled_publish')
    op.drop_column('properties', 'date_scheduled_retract')
