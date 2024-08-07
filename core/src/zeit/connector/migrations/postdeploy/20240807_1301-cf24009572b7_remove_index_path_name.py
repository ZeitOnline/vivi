"""remove index path name

Revision ID: cf24009572b7
Revises: 6a09ae3f8778
Create Date: 2024-08-07 13:01:44.471318
"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'cf24009572b7'
down_revision: Union[str, None] = '6a09ae3f8778'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            'ix_properties_name',
            table_name='properties',
            postgresql_concurrently=True,
            if_exists=True,
        )


def downgrade() -> None:
    op.create_index('ix_properties_parent_path', 'properties', ['name'])
