from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from auth.dependencies import AccessTokenBearer, get_current_user
from schemas import CartItemCreate, CartItemResponse
from db.models import User
from cart.services import CartService
from typing import List

from db.session import get_session


Cart_router = APIRouter(prefix="/cart", tags=["Cart"])
cart_services= CartService()


@Cart_router.get("/", response_model=List[CartItemResponse])
async def get_cart_items(session: AsyncSession= Depends(get_session), token_details= Depends(AccessTokenBearer)):
    user_details:User| None = await get_current_user(token_details, session)
    return await cart_services.get_cart_items(user_details, session)


@Cart_router.post("/add")
async def add_to_cart(Items: CartItemCreate, session:AsyncSession=Depends(get_session), token_details= Depends(AccessTokenBearer)):
    user_details:User| None = await get_current_user(token_details, session)
    return await cart_services.add_to_cart(user_details, Items, session)


@Cart_router.delete("/{item_id}")
async def remove_from_cart():
    pass
