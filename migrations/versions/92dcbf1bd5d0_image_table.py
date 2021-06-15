"""image table

Revision ID: 92dcbf1bd5d0
Revises: 8b9341b8df10
Create Date: 2021-06-12 16:10:07.694814

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '92dcbf1bd5d0'
down_revision = '8b9341b8df10'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('image', sa.Column('data_set', sa.String(length=5), nullable=True))
    op.create_index(op.f('ix_image_data_set'), 'image', ['data_set'], unique=False)
    op.add_column('user', sa.Column('end_time', sa.DateTime(), nullable=True))
    op.add_column('user', sa.Column('start_time', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'start_time')
    op.drop_column('user', 'end_time')
    op.drop_index(op.f('ix_image_data_set'), table_name='image')
    op.drop_column('image', 'data_set')
    # ### end Alembic commands ###