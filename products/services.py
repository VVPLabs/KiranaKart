from uuid import UUID
from db.models import Product
from products.schemes import ProductCreate
from sqlmodel import select, desc
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import HTTPException, status

class ProductService:
    async def get_all_products(self, session:AsyncSession):
        try:
            statement = select(Product).order_by(desc(Product.created_at))
            result = await session.exec(statement)
            products = result.all()
            return products

        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"FAILED TO FETCH PRODUCTS: {str(e)}")

    async def create_new_product(self, session:AsyncSession, product_data:ProductCreate):
        product_data_dict= product_data.model_dump()

        new_product= Product(**product_data_dict)
        session.add(new_product)
        await session.commit()
        return new_product
