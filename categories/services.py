from fastapi import HTTPException, status
from db.models import Category
from categories.schemas import CategoryCreate
from sqlmodel.ext.asyncio.session import AsyncSession


class CategoryService:
    async def create_category(self, session:AsyncSession, category_data:CategoryCreate):
        try:
            category_data_dict= category_data.model_dump()
            new_category= Category(**category_data_dict)
            session.add(new_category)
            await session.commit()
            return new_category
        except Exception as e:
            await session.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={"Failed to create category."})


