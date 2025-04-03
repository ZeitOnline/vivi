"""add image_separately_purchased column

Revision ID: 2f7a8b0212ae
Revises: ef06d4a56605
Create Date: 2025-03-31 14:07:03.986842

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2f7a8b0212ae'
down_revision: Union[str, None] = 'ef06d4a56605'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'properties',
        sa.Column(
            'image_separately_purchased',
            sa.Boolean(),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column('properties', 'image_separately_purchased')
