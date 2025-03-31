"""create index for image_separately_purchased

Revision ID: 20a7ba9a2def
Revises: f83e173d7e5b
Create Date: 2025-03-31 14:07:43.479218

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '20a7ba9a2def'
down_revision: Union[str, None] = 'f83e173d7e5b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.create_index(
            op.f('ix_properties_image_separately_purchased'),
            'properties',
            ['image_separately_purchased'],
            postgresql_concurrently=True,
            if_not_exists=True,
        )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            op.f('ix_properties_image_separately_purchased'),
            'properties',
            ['image_separately_purchased'],
            postgresql_concurrently=True,
            if_exists=True,
        )
