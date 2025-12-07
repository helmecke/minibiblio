"""merge patron updates and user table

Revision ID: a55cdc127c38
Revises: 3a708b28b709, f1a2b3c4d5e6
Create Date: 2025-12-07 12:31:56.916760

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a55cdc127c38'
down_revision: Union[str, Sequence[str], None] = ('3a708b28b709', 'f1a2b3c4d5e6')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
