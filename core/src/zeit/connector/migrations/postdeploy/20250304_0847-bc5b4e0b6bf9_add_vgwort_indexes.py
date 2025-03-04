"""add vgwort indexes

Revision ID: bc5b4e0b6bf9
Revises: 54ab13b7094e
Create Date: 2025-03-04 08:47:27.354129

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'bc5b4e0b6bf9'
down_revision: Union[str, None] = '54ab13b7094e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

COLUMNS = ['vgwort_private_token', 'vgwort_reported_on', 'vgwort_reported_error']


def upgrade() -> None:
    with op.get_context().autocommit_block():
        for column in COLUMNS:
            op.create_index(
                f'ix_properties_{column}',
                'properties',
                [column],
                postgresql_concurrently=True,
                if_not_exists=True,
            )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        for column in COLUMNS:
            op.drop_index(
                f'ix_properties_{column}',
                table_name='properties',
                postgresql_concurrently=True,
                if_exists=True,
            )
