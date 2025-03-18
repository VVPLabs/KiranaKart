import uuid
from datetime import datetime, timezone
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from db.models import remove_timezone

from schemas import CartItemCreate
from db.models import Cart, CartItem, User

class CartService:
    async def get_cart_items(self, user_details:User|None, session:AsyncSession):
        if user_details:
            user_id= user_details.user_id
        statement= select(Cart).where(Cart.user_id == user_id)

        result = await session.exec(statement)
        cart = result.one_or_none()

        return cart.cart_items if cart else []

    async def add_to_cart(self, user_details: User|None, item: CartItemCreate, session:AsyncSession):
        if user_details:
            user_id= user_details.user_id

        statement= select(Cart).where(Cart.user_id == user_id)

        result = await session.exec(statement)
        cart = result.one_or_none()

        if not cart:
            cart = Cart(user_id=user_id)
            session.add(cart)
            await session.commit()
            await session.refresh(cart)

        statement = select(CartItem).where(
            (CartItem.cart_id == cart.cart_id) & (CartItem.product_id == item.product_id)
        )
        result = await session.exec(statement)
        existing_item = result.one_or_none()

        if existing_item:
            existing_item.quantity += item.quantity
            existing_item.updated_at = remove_timezone(datetime.now(timezone.utc))
        else:
            new_item = CartItem(cart_id=cart.cart_id, **item.model_dump())
            session.add(new_item)

        await session.commit()
        return existing_item or new_item

