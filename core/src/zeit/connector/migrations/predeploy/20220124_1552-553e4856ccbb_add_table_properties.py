"""add table properties

Revision ID: 553e4856ccbb
Revises:
Create Date: 2022-01-24 15:52:39

"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy.dialects.postgresql import JSONB
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '553e4856ccbb'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'properties',
        sa.Column('id', sa.Uuid(as_uuid=False), nullable=False),
        sa.Column('type', sa.Unicode(), server_default='unknown', nullable=False),
        sa.Column('is_collection', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('body', sa.UnicodeText(), nullable=True),
        sa.Column('unsorted', JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            'last_updated',
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_index(
        op.f('ix_properties_last_updated'), 'properties', ['last_updated'], unique=False
    )
    op.create_index(op.f('ix_properties_type'), 'properties', ['type'], unique=False)
    op.create_index(
        'ix_properties_unsorted',
        'properties',
        ['unsorted'],
        unique=False,
        postgresql_using='gin',
        postgresql_ops={'unsorted': 'jsonb_path_ops'},
    )


def downgrade() -> None:
    op.drop_index(
        'ix_properties_unsorted',
        table_name='properties',
        postgresql_using='gin',
        postgresql_ops={'unsorted': 'jsonb_path_ops'},
    )
    op.drop_index(op.f('ix_properties_type'), table_name='properties')
    op.drop_index(op.f('ix_properties_last_updated'), table_name='properties')

    op.drop_table('properties')
