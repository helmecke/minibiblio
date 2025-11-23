"""create loans table

Revision ID: 24c1ec790252
Revises: d5f9316aa91f
Create Date: 2025-11-22 20:35:22.417841

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '24c1ec790252'
down_revision: Union[str, Sequence[str], None] = 'd5f9316aa91f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create loans table."""
    op.create_table(
        'loans',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('loan_id', sa.String(20), nullable=False, unique=True, index=True),
        sa.Column('catalog_item_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('catalog_items.id'), nullable=False, index=True),
        sa.Column('patron_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('patrons.id'), nullable=False, index=True),
        sa.Column('checkout_date', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('due_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('return_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.Enum('active', 'returned', 'overdue', 'lost', name='loanstatus'), nullable=False, server_default='active', index=True),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    """Drop loans table."""
    op.drop_table('loans')
    op.execute('DROP TYPE IF EXISTS loanstatus')
