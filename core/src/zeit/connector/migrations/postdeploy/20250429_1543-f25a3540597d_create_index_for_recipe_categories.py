"""create index for recipe_categories and recipe_ingredients

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

COLUMNS = ['categories', 'ingredients']


def upgrade() -> None:
    with op.get_context().autocommit_block():
        for column in COLUMNS:
            op.create_index(
                f'ix_properties_recipe_{column}',
                'properties',
                [f'recipe_{column}'],
                unique=False,
                postgresql_using='gin',
                postgresql_ops={f'recipe_{column}': 'jsonb_path_ops'},
                postgresql_concurrently=True,
                if_not_exists=True,
            )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        for column in COLUMNS:
            op.drop_index(
                op.f(f'ix_properties_recipe_{column}'),
                'properties',
                [f'recipe_{column}'],
                postgresql_concurrently=True,
                if_exists=True,
            )
