"""add modified column

(was forgotten in b7304b8f2b06)

Revision ID: 28355ecfa735
Revises: b7304b8f2b06
Create Date: 2024-09-26 11:50:35.942786
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '28355ecfa735'
down_revision: Union[str, None] = 'b7304b8f2b06'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'properties', sa.Column('date_last_modified', sa.TIMESTAMP(timezone=True), nullable=True)
    )


def downgrade() -> None:
    op.drop_column('properties', 'date_last_modified')
