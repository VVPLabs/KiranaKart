from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from db.session import get_session
from typing import List
from products.schemes import ProductResponse, ProductCreate
from products.services import ProductService

Product_router = APIRouter(prefix="/products", tags=["Products"])
product_services= ProductService()

@Product_router.get("/", response_model=List[ProductResponse])
async def all_products(session:AsyncSession=Depends(get_session)):
    products_data = await product_services.get_all_products(session)
    return products_data


@Product_router.post("/")
async def add_product(products_data:ProductCreate):
    pass



@Product_router.get("/{product_id}")
async def show_product():
    pass




@Product_router.patch("/{Product_id}")
async def update_product():
    pass


@Product_router.delete("/{Product_id}")
async def delete_product():
    pass
