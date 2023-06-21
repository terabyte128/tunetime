"""add tokens

Revision ID: 55c0792da973
Revises: f4d9ef82fc1c
Create Date: 2023-06-19 23:23:16.775654

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '55c0792da973'
down_revision = 'f4d9ef82fc1c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('sessions', sa.Column('access_token', sa.String(), nullable=False))
    op.add_column('sessions', sa.Column('refresh_token', sa.String(), nullable=False))
    op.add_column('sessions', sa.Column('expires_at', sa.Integer(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('sessions', 'expires_at')
    op.drop_column('sessions', 'refresh_token')
    op.drop_column('sessions', 'access_token')
    # ### end Alembic commands ###