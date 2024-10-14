"""create index for channels

Revision ID: 6cc99f5afdc5
Revises: cf24009572b7
Create Date: 2024-09-12 10:58:00.181930

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '6cc99f5afdc5'
down_revision: Union[str, None] = 'cf24009572b7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.create_index(
            'ix_properties_channels',
            'properties',
            ['channels'],
            unique=False,
            postgresql_using='gin',
            postgresql_ops={'channels': 'jsonb_path_ops'},
            postgresql_concurrently=True,
            if_not_exists=True,
        )


def downgrade() -> None:
    op.drop_index('ix_properties_channels', table_name='properties', postgresql_using='gin')
