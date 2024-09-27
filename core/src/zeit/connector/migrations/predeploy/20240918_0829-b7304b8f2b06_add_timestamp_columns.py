"""add timestamp columns

Revision ID: b7304b8f2b06
Revises: 9aba9394d011
Create Date: 2024-09-18 08:29:25.572847

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b7304b8f2b06'
down_revision: Union[str, None] = '9aba9394d011'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'properties', sa.Column('date_created', sa.TIMESTAMP(timezone=True), nullable=True)
    )
    op.add_column(
        'properties', sa.Column('date_last_checkout', sa.TIMESTAMP(timezone=True), nullable=True)
    )
    op.add_column(
        'properties', sa.Column('date_first_released', sa.TIMESTAMP(timezone=True), nullable=True)
    )
    op.add_column(
        'properties', sa.Column('date_last_published', sa.TIMESTAMP(timezone=True), nullable=True)
    )
    op.add_column(
        'properties',
        sa.Column('date_last_published_semantic', sa.TIMESTAMP(timezone=True), nullable=True),
    )
    op.add_column(
        'properties', sa.Column('date_print_published', sa.TIMESTAMP(timezone=True), nullable=True)
    )
    op.add_column(
        'properties',
        sa.Column('date_last_modified_semantic', sa.TIMESTAMP(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column('properties', 'date_last_modified_semantic')
    op.drop_column('properties', 'date_print_published')
    op.drop_column('properties', 'date_last_published_semantic')
    op.drop_column('properties', 'date_last_published')
    op.drop_column('properties', 'date_first_released')
    op.drop_column('properties', 'date_last_checkout')
    op.drop_column('properties', 'date_created')
