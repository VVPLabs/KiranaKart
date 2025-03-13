from uuid import UUID
from db.models import Product, Category, ProductCategory
from products.schemes import ProductCreate
from categories.services import CategoryService
from sqlmodel import and_, select, desc
from sqlalchemy.orm import selectinload
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import HTTPException, status

category_services= CategoryService()

class ProductService:
    async def get_all_products(self, session:AsyncSession):
        try:
            statement = select(Product).options(selectinload(Product.categories)).order_by(desc(Product.created_at)) # type: ignore
            result = await session.exec(statement)
            products = result.all()
            return products

        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"FAILED TO FETCH PRODUCTS: {str(e)}")


    async def create_new_product(self, session:AsyncSession, product_data:ProductCreate):
        product_data_dict= product_data.model_dump()
        category_names = product_data_dict.pop("category_names", [])
        try:
            if not product_data.vendor_id:
                raise HTTPException(status_code=400, detail="Vendor ID is required")

            existing_product = await session.exec(
            select(Product).where(and_(
                Product.name == product_data.name,
                Product.vendor_id == product_data.vendor_id)
            ))
            if existing_product.first():
                raise HTTPException(status_code=400, detail="Product already exists")

            category_ids = []
            if category_names:
                result = await session.exec(select(Category).where(Category.category_name.in_(category_names))) # type: ignore
                categories = list(result.all())
                existing_names = {category.category_name for category in categories}
                missing_names = set(category_names) - existing_names
                new_categories = [Category(category_name=name) for name in missing_names]
                session.add_all(new_categories)
                await session.flush()
                categories.extend(new_categories)
                category_ids = [category.category_id for category in categories]

            new_product= Product(**product_data_dict)
            session.add(new_product)
            await session.flush()
            await session.refresh(new_product)

            for category_id in category_ids:
                product_category = ProductCategory(product_id=new_product.product_id, category_id=category_id)
                session.add(product_category)

            await session.commit()

            statement = (
            select(Product)
            .options(selectinload(Product.categories)) # type: ignore
            .where(Product.product_id == new_product.product_id)
        )
            result = await session.exec(statement)
            new_product_with_categories = result.one()
            return new_product_with_categories

        except Exception as e:
            await session.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"FAILED TO ADD PRODUCTS: {str(e)}")


    async def delete_product(self):
        pass
