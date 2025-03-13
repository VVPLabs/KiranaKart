from pydantic import BaseModel
from sqlmodel import Field
from db.models import ProductBase
from datetime import datetime
from typing import Optional, List
from uuid import UUID


class ProductCreate(ProductBase):
    category_ids: Optional[list[UUID]]


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = Field(default=None, ge=0)
    stock: Optional[int] = Field(default=None, ge=0)
    category_ids: Optional[List[UUID]] = None

class ProductCategoryLink(BaseModel):
    category_id: UUID
    category_name: str

class ProductResponse(ProductBase):
    product_id:UUID
    created_at:datetime
    categories:List[ProductCategoryLink]

class ProductListResponse(BaseModel):
    total:int
    products: ProductResponse