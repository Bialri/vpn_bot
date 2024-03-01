"""fix

Revision ID: 9de8af863b53
Revises: 7201476c8d65
Create Date: 2024-02-26 21:40:16.409084

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9de8af863b53'
down_revision: Union[str, None] = '7201476c8d65'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('vpn_profile', sa.Column('user_id', sa.Integer(), nullable=False))
    op.drop_constraint('vpn_profile_owner_id_fkey', 'vpn_profile', type_='foreignkey')
    op.create_foreign_key(None, 'vpn_profile', 'user', ['user_id'], ['id'])
    op.drop_column('vpn_profile', 'owner_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('vpn_profile', sa.Column('owner_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'vpn_profile', type_='foreignkey')
    op.create_foreign_key('vpn_profile_owner_id_fkey', 'vpn_profile', 'user', ['owner_id'], ['id'])
    op.drop_column('vpn_profile', 'user_id')
    # ### end Alembic commands ###
