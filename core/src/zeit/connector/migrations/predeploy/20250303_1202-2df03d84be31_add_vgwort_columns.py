"""add vgwort columns

Revision ID: 2df03d84be31
Revises: 57b3b2be21ef
Create Date: 2025-03-03 12:02:32.383049

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2df03d84be31'
down_revision: Union[str, None] = '57b3b2be21ef'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'properties', sa.Column('vgwort_reported_on', sa.TIMESTAMP(timezone=True), nullable=True)
    )
    op.add_column('properties', sa.Column('vgwort_reported_error', sa.Unicode(), nullable=True))
    op.add_column('properties', sa.Column('vgwort_public_token', sa.Unicode(), nullable=True))
    op.add_column('properties', sa.Column('vgwort_private_token', sa.Unicode(), nullable=True))


def downgrade() -> None:
    op.drop_column('properties', 'vgwort_private_token')
    op.drop_column('properties', 'vgwort_public_token')
    op.drop_column('properties', 'vgwort_reported_error')
    op.drop_column('properties', 'vgwort_reported_on')
