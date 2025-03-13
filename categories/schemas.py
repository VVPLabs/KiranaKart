from datetime import datetime
from products.schemes import ProductResponse
from db.models import CategoryBase
from sqlmodel import SQLModel
from typing import List, Optional
import uuid

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(SQLModel):
    name: Optional[str] = None
    parent_category_id: Optional[uuid.UUID] = None

class CategoryResponse(CategoryBase):
    category_id: uuid.UUID
    created_at: datetime

class CategoryResponseWithProducts(CategoryResponse):
    products: List[ProductResponse]=[]