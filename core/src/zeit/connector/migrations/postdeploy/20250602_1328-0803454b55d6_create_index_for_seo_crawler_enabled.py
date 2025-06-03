"""create index for seo_crawler_enabled

Revision ID: 0803454b55d6
Revises: f25a3540597d
Create Date: 2025-06-02 13:28:03.842852

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '0803454b55d6'
down_revision: Union[str, None] = 'f25a3540597d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.create_index(
            op.f('ix_properties_seo_crawler_enabled'),
            'properties',
            ['seo_crawler_enabled'],
            postgresql_concurrently=True,
            if_not_exists=True,
        )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            op.f('ix_properties_seo_crawler_enabled'),
            'properties',
            postgresql_concurrently=True,
            if_exists=True,
        )
