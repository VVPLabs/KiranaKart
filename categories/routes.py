from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from db.session import get_session
from categories.services import CategoryService
from categories.schemas import CategoryCreate, CategoryResponse


Category_router = APIRouter(prefix="/categories", tags=["Categories"])
category_services= CategoryService()

@Category_router.get("/")
async def get_all_categories():
    pass


@Category_router.post("/" , response_model=CategoryResponse)
async def create_category(category_data:CategoryCreate, session:AsyncSession= Depends(get_session)):
    new_category = await category_services.create_category(session, category_data)
    return new_category

@Category_router.get("/{category_id}")
async def get_category(categoty_id):
    pass