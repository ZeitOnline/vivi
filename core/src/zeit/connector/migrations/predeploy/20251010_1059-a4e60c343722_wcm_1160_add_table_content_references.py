"""WCM-1160: add table content_references

Revision ID: a4e60c343722
Revises: bc3c53852d3c
Create Date: 2025-10-10 10:59:03.938494

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a4e60c343722'
down_revision: Union[str, None] = 'bc3c53852d3c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'content_references',
        sa.Column('source', sa.Uuid(as_uuid=False), nullable=False),
        sa.Column('target', sa.Uuid(as_uuid=False), nullable=False),
        sa.Column('type', sa.Unicode(), nullable=False),
        sa.Column(
            'created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=True
        ),
        sa.ForeignKeyConstraint(['source'], ['properties.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['target'], ['properties.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('source', 'target', 'type'),
    )


def downgrade() -> None:
    op.drop_table('content_references')
