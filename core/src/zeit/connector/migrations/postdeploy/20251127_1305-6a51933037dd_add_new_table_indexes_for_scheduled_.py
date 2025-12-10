"""WCM-799: Add new table indexes for scheduled_operations

Revision ID: 6a51933037dd
Revises: fa922ea318ca
Create Date: 2025-11-27 13:05:31.609232

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '6a51933037dd'
down_revision: Union[str, None] = 'fa922ea318ca'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.create_index(
            'ix_scheduled_operations_pending',
            'scheduled_operations',
            ['executed_on', 'scheduled_on'],
            postgresql_concurrently=True,
            if_not_exists=True,
        )
        op.create_index(
            'ix_scheduled_operations_list',
            'scheduled_operations',
            ['content', 'operation'],
            postgresql_concurrently=True,
            if_not_exists=True,
        )
        op.create_index(
            'ix_scheduled_operations_content',
            'scheduled_operations',
            ['content'],
            postgresql_concurrently=True,
            if_not_exists=True,
        )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            op.f('ix_scheduled_operations_pending'),
            table_name='scheduled_operations',
            postgresql_concurrently=True,
            if_exists=True,
        )
        op.drop_index(
            op.f('ix_scheduled_operations_list'),
            table_name='scheduled_operations',
            postgresql_concurrently=True,
            if_exists=True,
        )
        op.drop_index(
            op.f('ix_scheduled_operations_content'),
            table_name='scheduled_operations',
            postgresql_concurrently=True,
            if_exists=True,
        )
