"""add table paths

Revision ID: 6392b9450475
Revises: 553e4856ccbb
Create Date: 2022-02-16 10:48:45

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6392b9450475'
down_revision: Union[str, None] = '553e4856ccbb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'paths',
        sa.Column('parent_path', sa.Unicode(), nullable=False),
        sa.Column('name', sa.Unicode(), nullable=False),
        sa.Column('id', sa.Uuid(as_uuid=False), nullable=False),
        sa.ForeignKeyConstraint(['id'], ['properties.id'], ondelete='cascade'),
        sa.PrimaryKeyConstraint('parent_path', 'name'),
        sa.UniqueConstraint('parent_path', 'name', 'id'),
    )

    op.create_index(op.f('ix_paths_id'), 'paths', ['id'], unique=False)
    op.create_index(op.f('ix_paths_parent_path'), 'paths', ['parent_path'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_paths_parent_path'), table_name='paths')
    op.drop_index(op.f('ix_paths_id'), table_name='paths')
    op.drop_table('paths')
