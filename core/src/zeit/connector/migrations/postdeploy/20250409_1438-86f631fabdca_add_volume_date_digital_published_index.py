"""add volume_date_digital_published index

Revision ID: 86f631fabdca
Revises: 20a7ba9a2def
Create Date: 2025-04-09 14:38:35.759114

"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import text as sql


# revision identifiers, used by Alembic.
revision: str = '86f631fabdca'
down_revision: Union[str, None] = '20a7ba9a2def'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

column = 'volume_date_digital_published'


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.create_index(
            f'ix_properties_{column}',
            'properties',
            [sql(f'{column} desc nulls last')],
            postgresql_concurrently=True,
            if_not_exists=True,
        )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            f'ix_properties_{column}',
            table_name='properties',
            postgresql_concurrently=True,
            if_exists=True,
        )
