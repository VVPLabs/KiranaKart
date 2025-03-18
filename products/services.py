from uuid import UUID
from db.models import Product, Category, ProductCategory
from products.schemes import ProductCreate, ProductResponse, ProductUpdate
from categories.services import CategoryService
from fastapi import UploadFile
from typing import List, Optional
from sqlmodel import and_, select, desc
from sqlalchemy.orm import selectinload
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.sql import func
from db.models import UserRole
from utils import image_up
import os
import json


from fastapi import HTTPException, status

category_services = CategoryService()


class ProductService:
    async def get_all_products(
        self, session: AsyncSession, limit: int = 5, cursor: UUID | None = None
    ):
        try:
            statement = select(Product).options(selectinload(Product.categories))  # type: ignore

            if cursor:
                statement = statement.where(Product.product_id < cursor)

            statement = statement.order_by(desc(Product.created_at)).limit(limit)

            result = await session.exec(statement)
            products = result.all()
            product_responses = [
                ProductResponse.model_validate(product) for product in products
            ]

            next_cursor = products[-1].product_id if len(products) == limit else None

            return {
                "products": product_responses,
                "limit": limit,
                "next_cursor": next_cursor,
            }

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"FAILED TO FETCH PRODUCTS: {str(e)}",
            )

    async def get_product(
        self,
        session: AsyncSession,
        product_query,
        limit: int = 5,
        cursor: UUID | None = None,
    ):
        try:
            statement = None
            try:
                product_uuid = UUID(product_query)
                statement = (
                    select(Product)
                    .options(selectinload(Product.categories))  # type: ignore
                    .where(Product.product_id == product_uuid)
                )

            except ValueError:
                # Not a valid UUID, perform a name search
                ts_query = func.plainto_tsquery("english", product_query)
                statement = (
                    select(Product)
                    .options(selectinload(Product.categories))  # type: ignore
                    .where(Product.name_tsv.op("@@")(ts_query))  # type: ignore
                    .order_by(
                        func.ts_rank_cd(Product.name_tsv, ts_query).desc()
                    )  # Rank results
                )
                if cursor:
                    statement = statement.where(Product.product_id < cursor)
                statement = statement.limit(limit)

            result = await session.exec(statement)
            product_data = result.all()

            if not product_data:
                category_ts_query = func.plainto_tsquery("english", product_query)
                category_statement = (
                    select(Product)
                    .join(Category, Product.categories)  # type: ignore
                    .where(Category.name_tsv.op("@@")(category_ts_query))  # type: ignore
                    .options(selectinload(Product.categories))  # type: ignore
                )
                if cursor:
                    category_statement = category_statement.where(
                        Product.product_id < cursor
                    )
                category_statement = category_statement.limit(limit)

                category_result = await session.exec(category_statement)
                product_data = category_result.all()

            next_cursor = (
                product_data[-1].product_id if len(product_data) == limit else None
            )
            product_responses = [
                ProductResponse.model_validate(product) for product in product_data
            ]
            return {
                "products": product_responses,
                "limit": limit,
                "next_cursor": next_cursor,  # Ideally, fetch total count separately if needed
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"FAILED TO FETCH PRODUCT: {str(e)}",
            )

    async def create_new_product(
        self, session: AsyncSession, product_data: ProductCreate,
    ):
        product_data_dict = product_data.model_dump()
        category_names = product_data_dict.pop("category_names", [])
        try:
            if not product_data.vendor_id:
                raise HTTPException(status_code=400, detail="Vendor ID is required")

            existing_product = await session.exec(
                select(Product).where(
                    and_(
                        Product.name == product_data.name,
                        Product.vendor_id == product_data.vendor_id,
                    )
                )
            )
            if existing_product.first():
                raise HTTPException(status_code=400, detail="Product already exists")

            category_ids = []
            if category_names:
                result = await session.exec(select(Category).where(Category.category_name.in_(category_names)))  # type: ignore
                categories = list(result.all())
                existing_names = {category.category_name for category in categories}
                missing_names = set(category_names) - existing_names
                new_categories = [
                    Category(category_name=name) for name in missing_names  # type: ignore
                ]
                session.add_all(new_categories)
                await session.flush()
                categories.extend(new_categories)
                category_ids = [category.category_id for category in categories]

            new_product = Product(**product_data_dict)
            session.add(new_product)
            await session.flush()
            await session.refresh(new_product)

            for category_id in category_ids:
                product_category = ProductCategory(
                    product_id=new_product.product_id, category_id=category_id
                )
                session.add(product_category)

            await session.commit()
            await session.refresh(new_product)

            statement = (
                select(Product)
                .options(selectinload(Product.categories))  # type: ignore
                .where(Product.product_id == new_product.product_id)
            )
            result = await session.exec(statement)
            new_product_with_categories = result.one()
            product_responses = [
                ProductResponse.model_validate(product)
                for product in new_product_with_categories
            ]
            return product_responses

        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"FAILED TO ADD PRODUCT: {str(e)}",
            )

    async def create_bulk_products(
        self, session: AsyncSession, products_data: List[ProductCreate]
    ):
        results = []
        errors = []
        for index, product_data in enumerate(products_data):
            try:
                product = await self.create_new_product(session, product_data)
                results.append({"index": index, "product": product})
            except HTTPException as e:
                errors.append({"index": index, "detail": e.detail})
            except Exception as e:
                errors.append({"index": index, "detail": f"Unexpected error: {str(e)}"})
        return {"success": results, "errors": errors}

    async def update_product(
        self,
        product_id,
        user_id,
        role,
        images,
        product_update_data: str,
        session: AsyncSession,
    ):
        try:
            update_data_dict = json.loads(product_update_data)  # Convert string to dictionary
            product_update = ProductUpdate(**update_data_dict)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON format")

        statement = select(Product).where(Product.product_id == product_id).options(selectinload(Product.categories))  # type: ignore
        product_to_update = await session.scalar(statement)

        if not product_to_update:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Product not found"
            )

        if UserRole.admin not in role and user_id != product_to_update.vendor_id:
            raise HTTPException(
                status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                detail="Only admins are allowed to update other vendor products",
            )
        for key, value in product_update.model_dump(exclude_unset=True).items():
            setattr(product_to_update, key, value)

        if images:
            image_urls = product_to_update.image_urls or []
            for image in images:
                image_url = await image_up.save_image(image, subdir=f"products/{product_id}")
                image_urls.append(image_url)
            product_to_update.image_urls = image_urls

        await session.commit()
        await session.refresh(product_to_update)

        product_response = ProductResponse.model_validate(product_to_update)
        return product_response

    async def delete_product(self, product_id, user_id, role, session: AsyncSession):
        statement = select(Product).where(Product.product_id == product_id)
        product_to_delete = await session.scalar(statement)
        if not product_to_delete:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
            )
        if UserRole.admin not in role and user_id != product_to_delete.vendor_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins or the product owner can delete this product",
            )
        if product_to_delete.image_urls:
            for urls in product_to_delete.image_urls:
                await image_up.delete_image(urls)

        await session.delete(product_to_delete)
        await session.commit()
        return {"message": "Product deleted successfully"}

    async def upload_images(
        self, session: AsyncSession, product_id: UUID, files: List[UploadFile]
    ) -> Optional[List[str]]:
        statement = select(Product).where(Product.product_id == product_id)
        product = await session.scalar(statement)

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        if not product.image_urls:
            product.image_urls = []

        new_image_urls = []
        for file in files:
            if not file.filename:
                raise HTTPException(status_code=400, detail="Invalid file")

            _, file_ext = os.path.splitext(file.filename)
            file_ext = file_ext.lower().lstrip(".")

            if file_ext not in {"jpg", "jpeg", "png"}:
                raise HTTPException(
                    status_code=400, detail=f"Invalid file format: {file_ext}"
                )

            image_url = await image_up.save_image(file, subdir=f"products/{product_id}")
            new_image_urls.append(image_url)

        if new_image_urls:
            product.image_urls = product.image_urls + new_image_urls

            await session.commit()
            await session.refresh(product)
        return product.image_urls
