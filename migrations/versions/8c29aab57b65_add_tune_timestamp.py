"""add tune timestamp

Revision ID: 8c29aab57b65
Revises: 6ef9b792cd48
Create Date: 2023-06-20 20:11:08.449388

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8c29aab57b65'
down_revision = '6ef9b792cd48'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tunes', sa.Column('created_at', sa.Integer(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('tunes', 'created_at')
    # ### end Alembic commands ###
