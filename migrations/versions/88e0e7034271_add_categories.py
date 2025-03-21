"""add categories

Revision ID: 88e0e7034271
Revises: a8283c83f453
Create Date: 2025-03-08 14:53:54.842604

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = "88e0e7034271"
down_revision: Union[str, None] = "a8283c83f453"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "category",
        sa.Column("category_id", sa.Uuid(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("parent_category_id", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["parent_category_id"],
            ["category.category_id"],
        ),
        sa.PrimaryKeyConstraint("category_id"),
    )
    op.add_column("cart", sa.Column("updated_at", sa.DateTime(), nullable=False))
    op.add_column("cartitem", sa.Column("updated_at", sa.DateTime(), nullable=False))
    op.add_column("orderitem", sa.Column("updated_at", sa.DateTime(), nullable=False))
    op.add_column("payment", sa.Column("updated_at", sa.DateTime(), nullable=False))
    op.drop_column("product", "category")
    op.add_column("review", sa.Column("updated_at", sa.DateTime(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("review", "updated_at")
    op.add_column(
        "product",
        sa.Column("category", sa.VARCHAR(), autoincrement=False, nullable=False),
    )
    op.drop_column("payment", "updated_at")
    op.drop_column("orderitem", "updated_at")
    op.drop_column("cartitem", "updated_at")
    op.drop_column("cart", "updated_at")
    op.drop_table("category")
    # ### end Alembic commands ###
