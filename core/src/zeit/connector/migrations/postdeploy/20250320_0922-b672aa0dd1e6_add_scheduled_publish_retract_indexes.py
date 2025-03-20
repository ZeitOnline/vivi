"""add scheduled publish/retract indexes

Revision ID: b672aa0dd1e6
Revises: 68d8321b6387
Create Date: 2025-03-20 09:22:32.748127

"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import text as sql


# revision identifiers, used by Alembic.
revision: str = 'b672aa0dd1e6'
down_revision: Union[str, None] = '68d8321b6387'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


COLUMNS = [
    'date_scheduled_publish',
    'date_scheduled_retract',
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
