"""add parent_path and name column

Revision ID: 5f2720a9a131
Revises: 6392b9450475
Create Date: 2024-07-08 13:22:50.728322

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5f2720a9a131'
down_revision: Union[str, None] = '6392b9450475'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('properties', sa.Column('parent_path', sa.Unicode(), nullable=True))
    op.add_column('properties', sa.Column('name', sa.Unicode(), nullable=True))


def downgrade() -> None:
    op.drop_column('properties', 'name')
    op.drop_column('properties', 'parent_path')
