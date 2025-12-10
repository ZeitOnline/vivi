"""WCM-799: Add new table scheduled_operations

Revision ID: 96836481e519
Revises: a4e60c343722
Create Date: 2025-11-27 12:58:01.855940

"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy.dialects import postgresql
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '96836481e519'
down_revision: Union[str, None] = 'a4e60c343722'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'scheduled_operations',
        sa.Column('id', sa.Uuid(as_uuid=False), nullable=False),
        sa.Column('content', sa.Uuid(as_uuid=False), nullable=False),
        sa.Column('operation', sa.Unicode(), nullable=False),
        sa.Column('scheduled_on', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('executed_on', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('property_changes', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_by', sa.Unicode(), nullable=False),
        sa.Column(
            'date_created',
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(['content'], ['properties.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    op.drop_table('scheduled_operations')
