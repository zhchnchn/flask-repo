"""add information columns for user model

Revision ID: f5a0e5d0065c
Revises: f212d77169e2
Create Date: 2018-01-25 16:32:05.536917

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f5a0e5d0065c'
down_revision = 'f212d77169e2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('about_me', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('last_seen', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('location', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('name', sa.String(length=64), nullable=True))
    op.add_column('users', sa.Column('register_time', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'register_time')
    op.drop_column('users', 'name')
    op.drop_column('users', 'location')
    op.drop_column('users', 'last_seen')
    op.drop_column('users', 'about_me')
    # ### end Alembic commands ###
