"""add categories to product

Revision ID: 000d3e1c46eb
Revises: 9d5d4e13bb08
Create Date: 2025-03-08 15:07:05.096515

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = "000d3e1c46eb"
down_revision: Union[str, None] = "9d5d4e13bb08"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "productcategory",
        sa.Column("product_id", sa.Uuid(), nullable=False),
        sa.Column("category_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["category_id"],
            ["category.category_id"],
        ),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["product.product_id"],
        ),
        sa.PrimaryKeyConstraint("product_id", "category_id"),
    )
    op.add_column(
        "product",
        sa.Column("category", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("product", "category")
    op.drop_table("productcategory")
    # ### end Alembic commands ###
