"""create catalog_items table

Revision ID: d5f9316aa91f
Revises: 8e0543dd7f8a
Create Date: 2025-11-22 20:14:40.346298

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'd5f9316aa91f'
down_revision: Union[str, Sequence[str], None] = '8e0543dd7f8a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create catalog_items table."""
    op.create_table(
        'catalog_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('catalog_id', sa.String(20), nullable=False, unique=True, index=True),
        sa.Column('type', sa.Enum('book', 'dvd', 'cd', 'magazine', 'other', name='catalogitemtype'), nullable=False, server_default='book', index=True),
        sa.Column('title', sa.String(500), nullable=False, index=True),
        sa.Column('author', sa.String(255), nullable=True, index=True),
        sa.Column('isbn', sa.String(20), nullable=True, index=True),
        sa.Column('publisher', sa.String(255), nullable=True),
        sa.Column('year', sa.Integer, nullable=True),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('genre', sa.String(100), nullable=True),
        sa.Column('language', sa.String(50), nullable=False, server_default='English'),
        sa.Column('location', sa.String(100), nullable=True),
        sa.Column('status', sa.Enum('available', 'borrowed', 'reserved', 'damaged', 'lost', name='catalogitemstatus'), nullable=False, server_default='available', index=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    """Drop catalog_items table."""
    op.drop_table('catalog_items')
    op.execute('DROP TYPE IF EXISTS catalogitemtype')
    op.execute('DROP TYPE IF EXISTS catalogitemstatus')
