"""create patrons table

Revision ID: 8e0543dd7f8a
Revises:
Create Date: 2025-11-22 19:44:36.220316

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '8e0543dd7f8a'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create patrons table."""
    op.create_table(
        'patrons',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('membership_id', sa.String(20), nullable=False, unique=True, index=True),
        sa.Column('first_name', sa.String(100), nullable=False),
        sa.Column('last_name', sa.String(100), nullable=False),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('phone', sa.String(50), nullable=True),
        sa.Column('status', sa.Enum('active', 'inactive', 'suspended', name='patronstatus'), nullable=False, server_default='active', index=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    """Drop patrons table."""
    op.drop_table('patrons')
    op.execute('DROP TYPE IF EXISTS patronstatus')
