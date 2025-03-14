from fastapi import APIRouter, Depends, Query, Body
from sqlmodel.ext.asyncio.session import AsyncSession
from db.session import get_session
from db.models import UserRole, User
from auth.dependencies import RoleChecker
from typing import List, Optional
from products.schemes import ProductResponse, ProductCreate, ProductUpdate
from products.services import ProductService
import uuid


Product_router = APIRouter(prefix="/products", tags=["Products"])
product_services = ProductService()


@Product_router.get("/")
async def all_products(
    session: AsyncSession = Depends(get_session),
    limit: int = Query(5, ge=1, le=100),  # Limit between 1 and 100
    cursor: Optional[uuid.UUID] = None,
):
    products_data = await product_services.get_all_products(session, limit=limit, cursor=cursor)
    return products_data


@Product_router.post("/", response_model=ProductResponse)
async def add_product(
    product_data: ProductCreate,
    session: AsyncSession = Depends(get_session),
    vendor: User = Depends(RoleChecker([UserRole.vendor])),
):
    product_data.vendor_id = vendor.user_id
    new_product = await product_services.create_new_product(session, product_data)
    return new_product

@Product_router.post("/bulk", response_model=dict)
async def add_products_bulk(
    products_data: list[ProductCreate],
    session: AsyncSession = Depends(get_session),
    vendor: User = Depends(RoleChecker([UserRole.vendor])),
):
    # Set vendor_id for all products
    for product_data in products_data:
        product_data.vendor_id = vendor.user_id

    result = await product_services.create_bulk_products(session, products_data)
    return result

@Product_router.get("/search/{product_query}")
async def show_product(
    product_query,
    session: AsyncSession = Depends(get_session),
    limit: int = Query(5, ge=1, le=100),  # Limit between 1 and 100
    cursor: Optional[uuid.UUID] = None,
):
    product = await product_services.get_product(session, product_query, limit=limit, cursor=cursor)
    return product


@Product_router.patch("/{product_id}")
async def update_product(product_id, product_update_data:ProductUpdate, session:AsyncSession= Depends(get_session), vendor: User = Depends(RoleChecker([UserRole.vendor, UserRole.admin]))):
    return await product_services.update_product(product_id, product_update_data, session)


@Product_router.delete("/{Product_id}")
async def delete_product():
    pass
