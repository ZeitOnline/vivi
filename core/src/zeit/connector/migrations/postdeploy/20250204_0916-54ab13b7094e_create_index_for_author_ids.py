"""create index for author ids

Revision ID: 54ab13b7094e
Revises: 239e72a15c2c
Create Date: 2025-02-04 09:16:44.143153
"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '54ab13b7094e'
down_revision: Union[str, None] = '239e72a15c2c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


COLUMNS = [
    'author_hdok_id',
    'author_ssoid',
]


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
