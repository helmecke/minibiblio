"""add_address_birthdate_to_patrons

Revision ID: 3a708b28b709
Revises: 22c0e88d5964
Create Date: 2025-11-25 19:47:24.328081

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3a708b28b709'
down_revision: Union[str, Sequence[str], None] = '22c0e88d5964'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add address column (Text, nullable)
    op.add_column('patrons', sa.Column('address', sa.Text(), nullable=True))

    # Add birthdate column (Date, nullable)
    op.add_column('patrons', sa.Column('birthdate', sa.Date(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove birthdate column
    op.drop_column('patrons', 'birthdate')

    # Remove address column
    op.drop_column('patrons', 'address')
