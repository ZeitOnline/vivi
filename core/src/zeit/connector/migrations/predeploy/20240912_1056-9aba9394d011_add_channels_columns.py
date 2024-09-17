"""add channels columns

Revision ID: 9aba9394d011
Revises: 5f2720a9a131
Create Date: 2024-09-12 10:56:52.266201

"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy.dialects.postgresql import JSONB
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9aba9394d011'
down_revision: Union[str, None] = '5f2720a9a131'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('properties', sa.Column('channels', JSONB(astext_type=sa.Text()), nullable=True))


def downgrade() -> None:
    op.drop_column('properties', 'channels')
