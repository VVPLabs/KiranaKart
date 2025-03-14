"""add FTS trigger for product name

Revision ID: cfd9cfab7850
Revises: c306ce44147c
Create Date: 2025-03-13 15:58:07.148456

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'cfd9cfab7850'
down_revision: Union[str, None] = 'c306ce44147c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('product', sa.Column('name_tsv', postgresql.TSVECTOR(), nullable=True))
    op.create_index(op.f('ix_product_name_tsv'), 'product', ['name_tsv'], unique=False, postgresql_using='gin')

    # Create a trigger function to update name_tsv automatically
    op.execute("""
        CREATE FUNCTION update_product_tsvector() RETURNS trigger AS $$
        BEGIN
            NEW.name_tsv := to_tsvector('english', NEW.name);
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Attach trigger to the product table
    op.execute("""
        CREATE TRIGGER product_tsv_update BEFORE INSERT OR UPDATE
        ON product FOR EACH ROW EXECUTE FUNCTION update_product_tsvector();
    """)

    # Populate existing records
    op.execute("UPDATE product SET name_tsv = to_tsvector('english', name);")


    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user', 'role',
               existing_type=postgresql.ENUM('admin', 'vendor', 'user', name='userrole'),
               nullable=True)
    op.drop_index(op.f('ix_product_name_tsv'), table_name='product')
    op.drop_column('product', 'name_tsv')
    # ### end Alembic commands ###
