"""add index parent_path pattern

Revision ID: 6a09ae3f8778
Revises: a23f8cf445b2
Create Date: 2024-08-07 12:54:28.103201
"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '6a09ae3f8778'
down_revision: Union[str, None] = 'a23f8cf445b2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.create_index(
            'ix_properties_parent_path_pattern',
            'properties',
            ['parent_path'],
            postgresql_ops={'parent_path': 'varchar_pattern_ops'},
            postgresql_concurrently=True,
            if_not_exists=True,
        )
        op.drop_index(
            'ix_properties_parent_path',
            table_name='properties',
            postgresql_concurrently=True,
            if_exists=True,
        )


def downgrade() -> None:
    op.drop_index('ix_properties_parent_path_pattern', table_name='properties')
    op.create_index('ix_properties_parent_path', 'properties', ['parent_path'])
