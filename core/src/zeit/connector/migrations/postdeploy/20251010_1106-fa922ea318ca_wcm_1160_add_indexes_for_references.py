"""WCM-1160: add indexes for references

Revision ID: fa922ea318ca
Revises: e9b9c6f6bb1d
Create Date: 2025-10-10 11:06:58.596776

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'fa922ea318ca'
down_revision: Union[str, None] = 'e9b9c6f6bb1d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.create_index(
            op.f('ix_content_references_target'),
            'content_references',
            ['target'],
            unique=False,
            postgresql_concurrently=True,
            if_not_exists=True,
        )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            'ix_content_references_target',
            table_name='content_references',
            postgresql_concurrently=True,
            if_exists=True,
        )
