"""create index for author_lastname

Revision ID: 68d8321b6387
Revises: bc5b4e0b6bf9
Create Date: 2025-03-05 09:15:35.884428

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from zeit.connector.models import CREATE_EXTENSION_UNACCENT


# revision identifiers, used by Alembic.
revision: str = '68d8321b6387'
down_revision: Union[str, None] = 'bc5b4e0b6bf9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(CREATE_EXTENSION_UNACCENT)

    with op.get_context().autocommit_block():
        op.create_index(
            'ix_properties_author_lastname',
            'properties',
            [sa.func.iunaccent(sa.Column('author_lastname'))],
            postgresql_where=sa.text("type='author'"),
            postgresql_ops={'parent_path': 'varchar_pattern_ops'},
            postgresql_concurrently=True,
            if_not_exists=True,
        )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            'ix_properties_author_lastname',
            table_name='properties',
            postgresql_concurrently=True,
            if_exists=True,
        )
