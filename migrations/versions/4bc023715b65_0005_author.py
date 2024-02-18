"""0005 Author

Revision ID: 4bc023715b65
Revises: 
Create Date: 2024-02-18 22:57:23.960883

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4bc023715b65'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('authors',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=32), server_default='name', nullable=False),
    sa.Column('surname', sa.String(length=32), server_default='nosurname', nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name', 'surname', name='_full_name')
    )
    op.create_table('quote',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('author_id', sa.Integer(), nullable=False),
    sa.Column('text', sa.String(length=255), nullable=False),
    sa.Column('raiting', sa.Integer(), server_default='3', nullable=False),
    sa.ForeignKeyConstraint(['author_id'], ['authors.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('quote')
    op.drop_table('authors')
    # ### end Alembic commands ###