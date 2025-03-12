from pydantic import BaseModel
from sqlmodel import Field
from db.models import ProductBase
from datetime import datetime
from typing import Optional
from uuid import UUID


class ProductCreate(BaseModel):
    name: str= Field(..., title="Product Name", min_length=2, max_length=255)
    description: str= Field(..., title="Product Description", min_length=10)
    category_ids: Optional[list[UUID]]
    price: float = Field(ge=0)
    stock: int = Field(ge=0)


class ProductResponse(ProductBase):
    pass