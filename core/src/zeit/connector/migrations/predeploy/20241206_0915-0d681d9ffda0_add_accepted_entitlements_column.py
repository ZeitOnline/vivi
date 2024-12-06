"""add accepted_entitlements column

Revision ID: 0d681d9ffda0
Revises: fb15e09b44f8
Create Date: 2024-12-06 09:15:44.934493

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0d681d9ffda0'
down_revision: Union[str, None] = 'fb15e09b44f8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('properties', sa.Column('accepted_entitlements', sa.Unicode(), nullable=True))


def downgrade() -> None:
    op.drop_column('properties', 'accepted_entitlements')
