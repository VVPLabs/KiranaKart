from typing import List, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field

# ----------------- CartItem Schemas -----------------#
class CartItemBase(BaseModel):
    product_id: UUID
    quantity: int = Field(default=1, ge=1)

class CartItemCreate(CartItemBase):
    pass

class CartItemUpdate(BaseModel):
    quantity: int = Field(ge=1)

class CartItemResponse(CartItemBase):
    cart_item_id: UUID
    cart_id: UUID
    updated_at: datetime

    class Config:
        from_attributes = True


# ----------------- Cart Schemas -----------------#
class CartBase(BaseModel):
    user_id: UUID

class CartCreate(CartBase):
    pass

class CartResponse(CartBase):
    cart_id: UUID
    created_at: datetime
    updated_at: datetime
    cart_items: List[CartItemResponse] = []

    class Config:
        from_attributes = True
