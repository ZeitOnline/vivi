"""WCM-445_gallery_type_column

Revision ID: 5b7b220c8c5a
Revises: cbac9954ed68
Create Date: 2024-10-15 11:28:34.505216

"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy import text as sql


# revision identifiers, used by Alembic.
revision: str = '5b7b220c8c5a'
down_revision: Union[str, None] = 'cbac9954ed68'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.create_index(
            'ix_properties_gallery_type',
            'properties',
            [sql('gallery_type')],
            postgresql_concurrently=True,
            if_not_exists=True,
        )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            'ix_properties_gallery_type',
            table_name='properties',
            postgresql_concurrently=True,
            if_exists=True,
        )
