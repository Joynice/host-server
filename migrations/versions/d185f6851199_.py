"""empty message

Revision ID: d185f6851199
Revises: de3f068c83f3
Create Date: 2019-04-10 15:15:33.732829

"""

# revision identifiers, used by Alembic.
revision = 'd185f6851199'
down_revision = 'de3f068c83f3'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('asset', sa.Column('url', sa.String(length=255), nullable=False))
    op.drop_constraint('asset_ibfk_1', 'asset', type_='foreignkey')
    op.drop_column('asset', 'url_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('asset', sa.Column('url_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True))
    op.create_foreign_key('asset_ibfk_1', 'asset', 'task', ['url_id'], ['id'])
    op.drop_column('asset', 'url')
    # ### end Alembic commands ###