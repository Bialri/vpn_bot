"""empty message

Revision ID: 910d395cb525
Revises: 6e58015b0927
Create Date: 2024-03-08 15:28:56.001693

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '910d395cb525'
down_revision: Union[str, None] = '6e58015b0927'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('vpn_interfaces', sa.Column('server', sa.String(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('vpn_interfaces', 'server')
    # ### end Alembic commands ###