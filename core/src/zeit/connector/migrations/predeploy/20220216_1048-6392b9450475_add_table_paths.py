"""add table paths and locks

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

    op.create_table(
        'locks',
        sa.Column(
            'id',
            sa.Uuid(as_uuid=False),
            sa.ForeignKey('properties.id'),
            nullable=False,
            primary_key=True,
        ),
        sa.Column('principal', sa.Unicode(), nullable=False),
        sa.Column('until', sa.TIMESTAMP(timezone=True), nullable=False),
    )

    with op.get_context().autocommit_block():
        op.create_index(
            op.f('ix_paths_id'),
            'paths',
            ['id'],
            unique=False,
            postgresql_concurrently=True,
            if_not_exists=True,
        )
        op.create_index(
            op.f('ix_paths_parent_path'),
            'paths',
            ['parent_path'],
            unique=False,
            postgresql_concurrently=True,
            if_not_exists=True,
        )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            op.f('ix_paths_parent_path'),
            table_name='paths',
            postgresql_concurrently=True,
            if_exists=True,
        )
        op.drop_index(
            op.f('ix_paths_id'),
            table_name='paths',
            postgresql_concurrently=True,
            if_exists=True,
        )
    op.drop_table('locks')
    op.drop_table('paths')
