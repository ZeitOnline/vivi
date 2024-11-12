"""WCM-471: raw query columns

Revision ID: b6c4f9badee3
Revises: cbac9954ed68
Create Date: 2024-11-11 13:59:09.102738

"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import text as sql


# revision identifiers, used by Alembic.
revision: str = 'b6c4f9badee3'
down_revision: Union[str, None] = 'cbac9954ed68'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.create_index(
            'ix_properties_audio_premium_enabled',
            'properties',
            [sql('audio_premium_enabled')],
            postgresql_concurrently=True,
            if_not_exists=True,
        )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            'ix_properties_audio_premium_enabled',
            table_name='properties',
            postgresql_concurrently=True,
            if_exists=True,
        )
