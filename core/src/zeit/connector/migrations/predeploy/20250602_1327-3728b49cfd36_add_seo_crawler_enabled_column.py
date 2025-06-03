"""add seo_crawler_enabled column

Revision ID: 3728b49cfd36
Revises: 3a9f29f55c53
Create Date: 2025-06-02 13:27:12.525013

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3728b49cfd36'
down_revision: Union[str, None] = '3a9f29f55c53'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'properties',
        sa.Column(
            'seo_crawler_enabled',
            sa.Boolean(),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column('properties', 'seo_crawler_enabled')
