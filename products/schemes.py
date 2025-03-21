from sqlmodel import SQLModel
from sqlmodel import Field
from db.models import ProductBase
from datetime import datetime
from typing import Optional, List
from uuid import UUID


class ProductCreate(ProductBase):
    category_names: Optional[List[str]]
    vendor_id: Optional[UUID] = None


class ProductUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = Field(default=None, ge=0)
    stock: Optional[int] = Field(default=None, ge=0)
    category_names: Optional[List[str]] = None
    image_urls: Optional[List[str]] = None



class ProductCategoryLink(SQLModel):
    category_id: UUID
    category_name: str


class ProductResponse(ProductBase):
    product_id: UUID
    created_at: datetime
    categories: List[ProductCategoryLink]
    image_urls: Optional[List[str]]= []


class ProductListResponse(SQLModel):
    total: int
    products: ProductResponse
