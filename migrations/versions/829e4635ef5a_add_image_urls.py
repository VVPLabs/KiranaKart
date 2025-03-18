"""add image urls

Revision ID: 829e4635ef5a
Revises: ee0378713686
Create Date: 2025-03-17 14:20:49.569435

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '829e4635ef5a'
down_revision: Union[str, None] = 'ee0378713686'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('category', sa.Column('image_url', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    op.add_column('product', sa.Column('image_urls', sa.JSON(), nullable=True))
    op.add_column('user', sa.Column('image_url', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    op.alter_column('user', 'role',
               existing_type=postgresql.ENUM('admin', 'vendor', 'user', name='userrole'),
               nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user', 'role',
               existing_type=postgresql.ENUM('admin', 'vendor', 'user', name='userrole'),
               nullable=True)
    op.drop_column('user', 'image_url')
    op.drop_column('product', 'image_urls')
    op.drop_column('category', 'image_url')
    # ### end Alembic commands ###
