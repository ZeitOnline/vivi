"""create index for date_first_released_kpi_shard

Revision ID: 5aa8c611b3da
Revises: 0803454b55d6
Create Date: 2025-07-15 16:45:22.520110

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from zeit.connector.models import SQL_FUNCTIONS


# revision identifiers, used by Alembic.
revision: str = '5aa8c611b3da'
down_revision: Union[str, None] = '0803454b55d6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(SQL_FUNCTIONS['date_part'])

    with op.get_context().autocommit_block():
        op.create_index(
            'ix_properties_date_first_released_kpi_shard',
            'properties',
            [
                sa.func.idate_part('day', sa.Column('date_first_released')),
                sa.func.idate_part('hour', sa.Column('date_first_released')),
            ],
            postgresql_concurrently=True,
            if_not_exists=True,
        )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            'ix_properties_date_first_released_kpi_shard',
            table_name='properties',
            postgresql_concurrently=True,
            if_exists=True,
        )
