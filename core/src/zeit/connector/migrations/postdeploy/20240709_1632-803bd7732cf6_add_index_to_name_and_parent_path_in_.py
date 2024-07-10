"""add index to name and parent_path in content table

Revision ID: 803bd7732cf6
Revises:
Create Date: 2024-07-09 16:32:56.315221

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '803bd7732cf6'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.create_index(
            op.f('ix_properties_name'),
            'properties',
            ['name'],
            unique=False,
            postgresql_concurrently=True,
        )
        op.create_index(
            op.f('ix_properties_parent_path'),
            'properties',
            ['parent_path'],
            unique=False,
            postgresql_concurrently=True,
        )
        op.create_index(
            op.f('ix_properties_parent_path_name'),
            'properties',
            ['parent_path', 'name'],
            unique=True,
            postgresql_concurrently=True,
        )


def downgrade() -> None:
    op.drop_index(op.f('ix_properties_parent_path_name'), table_name='properties')
    op.drop_index(op.f('ix_properties_parent_path'), table_name='properties')
    op.drop_index(op.f('ix_properties_name'), table_name='properties')
