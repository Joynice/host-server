"""empty message

Revision ID: 0138e20bd617
Revises: afd9b3d2d0c3
Create Date: 2019-04-06 12:07:15.320546

"""

# revision identifiers, used by Alembic.
revision = '0138e20bd617'
down_revision = 'afd9b3d2d0c3'

from alembic import op
import sqlalchemy as sa


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('test_website',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('manufacturerUrl', sa.String(length=255), nullable=False),
    sa.Column('manufacturerName', sa.String(length=50), nullable=True),
    sa.Column('name', sa.String(length=50), nullable=True),
    sa.Column('url', sa.String(length=255), nullable=False),
    sa.Column('re', sa.String(length=255), nullable=True),
    sa.Column('md5', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('test_website')
    # ### end Alembic commands ###
