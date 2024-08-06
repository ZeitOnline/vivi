"""remove table paths

Revision ID: a23f8cf445b2
Revises: 803bd7732cf6
Create Date: 2024-08-06 13:32:37.001503
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a23f8cf445b2'
down_revision: Union[str, None] = '803bd7732cf6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            'ix_paths_id',
            table_name='paths',
            postgresql_concurrently=True,
            if_exists=True,
        )
        op.drop_index(
            'ix_paths_parent_path',
            table_name='paths',
            postgresql_concurrently=True,
            if_exists=True,
        )
        op.execute(sa.text('DROP TABLE IF EXISTS paths'))


def downgrade() -> None:
    pass  # an actual downgrade would have to restore all the data as well
