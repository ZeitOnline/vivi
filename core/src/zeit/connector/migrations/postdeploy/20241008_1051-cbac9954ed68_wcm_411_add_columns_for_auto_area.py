"""wcm_411_add_columns_for_auto_area

Revision ID: cbac9954ed68
Revises: a4c1b7f678d9
Create Date: 2024-10-08 10:51:56.065240

"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy import text as sql


# revision identifiers, used by Alembic.
revision: str = 'cbac9954ed68'
down_revision: Union[str, None] = 'a4c1b7f678d9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


COLUMNS = [
    'access',
    'article_genre',
    'print_ressort',
    'product',
    'published',
    'ressort',
    'series',
    'sub_ressort',
    'volume_year',
    'volume_number',
]


def upgrade() -> None:
    with op.get_context().autocommit_block():
        for column in COLUMNS:
            op.create_index(
                f'ix_properties_{column}',
                'properties',
                [sql(f'{column}')],
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
