"""Locality dept. ID nullable

Revision ID: 45abb24d82b8
Revises: 339c728950cb
Create Date: 2019-04-11 15:08:55.603457

"""
from alembic import op
import sqlalchemy as sa
import geoalchemy2


# revision identifiers, used by Alembic.
revision = '45abb24d82b8'
down_revision = '339c728950cb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('georef_localidades', 'departamento_id',
               existing_type=sa.VARCHAR(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('georef_localidades', 'departamento_id',
               existing_type=sa.VARCHAR(),
               nullable=False)
    # ### end Alembic commands ###