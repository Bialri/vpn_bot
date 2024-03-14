"""empty message

Revision ID: ae56eb2c8653
Revises: 45c8403c9461
Create Date: 2024-03-09 22:29:08.716922

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ae56eb2c8653'
down_revision: Union[str, None] = '45c8403c9461'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('last_action', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'last_action')
    # ### end Alembic commands ###