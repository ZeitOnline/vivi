"""create index for audio_type

Revision ID: f83e173d7e5b
Revises: f691fb06fe32
Create Date: 2025-03-31 13:29:43.984140

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'f83e173d7e5b'
down_revision: Union[str, None] = 'f691fb06fe32'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.create_index(
            op.f('ix_properties_audio_type'),
            'properties',
            ['audio_type'],
            postgresql_concurrently=True,
            if_not_exists=True,
        )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            op.f('ix_properties_audio_type'),
            'properties',
            ['audio_type'],
            postgresql_concurrently=True,
            if_exists=True,
        )
