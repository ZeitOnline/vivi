"""create index for timestamps

Revision ID: a4c1b7f678d9
Revises: 6cc99f5afdc5
Create Date: 2024-09-25 16:30:59.236538

"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import text as sql


# revision identifiers, used by Alembic.
revision: str = 'a4c1b7f678d9'
down_revision: Union[str, None] = '6cc99f5afdc5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


COLUMNS = [
    'date_last_modified_semantic',
    'date_last_published',
    'date_last_published_semantic',
    'date_first_released',
]


def upgrade() -> None:
    with op.get_context().autocommit_block():
        for column in COLUMNS:
            op.create_index(
                f'ix_properties_{column}',
                'properties',
                [sql(f'{column} desc nulls last')],
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
