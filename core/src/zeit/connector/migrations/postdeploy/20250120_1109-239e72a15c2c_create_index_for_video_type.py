"""create index for video_type

Revision ID: 239e72a15c2c
Revises: b6c4f9badee3
Create Date: 2025-01-20 11:09:46.675290

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '239e72a15c2c'
down_revision: Union[str, None] = 'b6c4f9badee3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.create_index(
            op.f('ix_properties_video_type'),
            'properties',
            ['video_type'],
            postgresql_concurrently=True,
            if_not_exists=True,
        )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            op.f('ix_properties_video_type'),
            'properties',
            ['video_type'],
            postgresql_concurrently=True,
            if_exists=True,
        )
