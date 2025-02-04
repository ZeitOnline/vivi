"""add author columns

Revision ID: 57b3b2be21ef
Revises: f7f17b16292c
Create Date: 2025-02-04 09:13:10.886349
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '57b3b2be21ef'
down_revision: Union[str, None] = 'f7f17b16292c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('properties', sa.Column('author_firstname', sa.Unicode(), nullable=True))
    op.add_column('properties', sa.Column('author_lastname', sa.Unicode(), nullable=True))
    op.add_column('properties', sa.Column('author_displayname', sa.Unicode(), nullable=True))
    op.add_column('properties', sa.Column('author_initials', sa.Unicode(), nullable=True))
    op.add_column('properties', sa.Column('author_department', sa.Unicode(), nullable=True))
    op.add_column('properties', sa.Column('author_ssoid', sa.Integer(), nullable=True))
    op.add_column('properties', sa.Column('author_hdok_id', sa.Integer(), nullable=True))
    op.add_column('properties', sa.Column('author_vgwort_id', sa.Integer(), nullable=True))
    op.add_column('properties', sa.Column('author_vgwort_code', sa.Unicode(), nullable=True))


def downgrade() -> None:
    op.drop_column('properties', 'author_vgwort_code')
    op.drop_column('properties', 'author_vgwort_id')
    op.drop_column('properties', 'author_hdok_id')
    op.drop_column('properties', 'author_ssoid')
    op.drop_column('properties', 'author_department')
    op.drop_column('properties', 'author_initials')
    op.drop_column('properties', 'author_displayname')
    op.drop_column('properties', 'author_lastname')
    op.drop_column('properties', 'author_firstname')
