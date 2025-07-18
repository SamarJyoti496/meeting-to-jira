"""Make priority column nullable in requirements table

Revision ID: 1be52a56ca62
Revises: bbb285628137
Create Date: 2025-07-12 20:51:13.318517

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1be52a56ca62'
down_revision: Union[str, Sequence[str], None] = 'bbb285628137'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('requirements', 'priority',
               existing_type=sa.VARCHAR(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('requirements', 'priority',
               existing_type=sa.VARCHAR(),
               nullable=False)
    # ### end Alembic commands ###
