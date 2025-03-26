"""Add article_template column

Revision ID: 0ebf5005eb51
Revises: b672aa0dd1e6
Create Date: 2025-03-25 15:43:38.883978

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '0ebf5005eb51'
down_revision: Union[str, None] = 'b672aa0dd1e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.create_index(
            'ix_properties_article_template',
            'properties',
            ['article_template'],
            unique=False,
            postgresql_concurrently=True,
            if_not_exists=True,
        )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            'ix_properties_article_template',
            table_name='properties',
            postgresql_concurrently=True,
            if_exists=True,
        )
