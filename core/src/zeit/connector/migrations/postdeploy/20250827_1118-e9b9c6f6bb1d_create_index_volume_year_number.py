"""create index volume_year_number

Revision ID: e9b9c6f6bb1d
Revises: 5aa8c611b3da
Create Date: 2025-08-27 11:18:50.003970

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'e9b9c6f6bb1d'
down_revision: Union[str, None] = '5aa8c611b3da'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.create_index(
            'ix_properties_volume_year_number',
            'properties',
            ['volume_year', 'volume_number'],
            postgresql_concurrently=True,
            if_not_exists=True,
        )

        op.drop_index(
            'ix_properties_volume_year',
            table_name='properties',
            postgresql_concurrently=True,
            if_exists=True,
        )
        op.drop_index(
            'ix_properties_volume_number',
            table_name='properties',
            postgresql_concurrently=True,
            if_exists=True,
        )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.create_index(
            'ix_properties_volume_year',
            'properties',
            ['volume_year'],
            postgresql_concurrently=True,
            if_not_exists=True,
        )
        op.create_index(
            'ix_properties_volume_number',
            'properties',
            ['volume_number'],
            postgresql_concurrently=True,
            if_not_exists=True,
        )

        op.drop_index(
            'ix_properties_volume_year_number',
            table_name='properties',
            postgresql_concurrently=True,
            if_exists=True,
        )
