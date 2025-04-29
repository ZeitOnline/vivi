"""create index for recipe_categories

Revision ID: f25a3540597d
Revises: 86f631fabdca
Create Date: 2025-04-29 15:43:17.999832

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'f25a3540597d'
down_revision: Union[str, None] = '86f631fabdca'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.create_index(
            'ix_properties_recipe_categories',
            'properties',
            ['recipe_categories'],
            unique=False,
            postgresql_using='gin',
            postgresql_ops={'recipe_categories': 'jsonb_path_ops'},
            postgresql_concurrently=True,
            if_not_exists=True,
        )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            op.f('ix_properties_recipe_categories'),
            'properties',
            ['recipe_categories'],
            postgresql_concurrently=True,
            if_exists=True,
        )
