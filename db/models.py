import uuid
from sqlmodel import SQLModel, Field, Relationship, JSON
from typing import Optional, List
from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import TSVECTOR, UUID
from datetime import datetime, timezone
from enum import Enum


def remove_timezone(dt: datetime) -> datetime:

    return dt.replace(tzinfo=None) if dt.tzinfo else dt


# ------------------- User ---------------------#


class UserRole(str, Enum):
    admin = "admin"
    vendor = "vendor"
    user = "user"


class UserBase(SQLModel):
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class User(UserBase, table=True):
    user_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    role: UserRole = Field(default=UserRole.user)
    is_verified: bool = Field(default=False)
    is_active: bool = Field(default=True)
    password_hash: str = Field(exclude=True)
    image_url: Optional[str] = None

    created_at: datetime = Field(
        default_factory=lambda: remove_timezone(datetime.now(timezone.utc))
    )
    updated_at: datetime = Field(
        default_factory=lambda: remove_timezone(datetime.now(timezone.utc))
    )
    deleted_at: Optional[datetime] = None

    products: List["Product"] = Relationship(
        back_populates="vendor",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )

    orders: List["Order"] = Relationship(back_populates="user")
    reviews: List["Review"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    cart: Optional["Cart"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


# ------------------ Product-Category Association Table ---------------------#
class ProductCategory(SQLModel, table=True):
    product_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("product.product_id", ondelete="CASCADE"),
            primary_key=True,
        )
    )
    category_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("category.category_id", ondelete="CASCADE"),
            primary_key=True,
        )
    )
    created_at: datetime = Field(
        default_factory=lambda: remove_timezone(datetime.now(timezone.utc))
    )


# ------------------- Product ---------------------#
class ProductBase(SQLModel):
    name: str
    description: str
    price: float = Field(ge=0)
    stock: int = Field(ge=0)


class Product(ProductBase, table=True):
    product_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    vendor_id: uuid.UUID = Field(foreign_key="user.user_id", nullable=False)
    created_at: datetime = Field(
        default_factory=lambda: remove_timezone(datetime.now(timezone.utc))
    )
    updated_at: datetime = Field(
        default_factory=lambda: remove_timezone(datetime.now(timezone.utc))
    )
    image_urls: Optional[List[str]] = Field(default=[], sa_column=Column(JSON))
    name_tsv: str = Field(sa_column=Column(TSVECTOR, index=True))

    categories: List["Category"] = Relationship(
        back_populates="products",
        link_model=ProductCategory,
        sa_relationship_kwargs={"passive_deletes": True},

    )
    vendor: Optional["User"] = Relationship(back_populates="products")

    order_items: List["OrderItem"] = Relationship(
        back_populates="product",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    cart_items: List["CartItem"] = Relationship(
        back_populates="product",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    reviews: List["Review"] = Relationship(
        back_populates="product",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


# ------------------- Order ---------------------#
class OrderStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    shipped = "shipped"
    delivered = "delivered"


class OrderBase(SQLModel):
    status: OrderStatus = Field(default=OrderStatus.pending)
    total: float = Field(ge=0)


class Order(OrderBase, table=True):
    order_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: Optional[uuid.UUID] = Field(
        foreign_key="user.user_id", index=True, nullable=True
    )
    created_at: datetime = Field(
        default_factory=lambda: remove_timezone(datetime.now(timezone.utc))
    )
    updated_at: datetime = Field(
        default_factory=lambda: remove_timezone(datetime.now(timezone.utc))
    )

    user: Optional["User"] = Relationship(back_populates="orders")
    order_items: List["OrderItem"] = Relationship(
        back_populates="order", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    payment: Optional["Payment"] = Relationship(
        back_populates="order", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


# ----------------- OrderItem ---------------------#
class OrderItemBase(SQLModel):
    quantity: int = Field(ge=1)
    price: float = Field(ge=0)


class OrderItem(OrderItemBase, table=True):
    order_item_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    order_id: uuid.UUID = Field(foreign_key="order.order_id", index=True)
    product_id: uuid.UUID = Field(foreign_key="product.product_id", index=True)
    updated_at: datetime = Field(
        default_factory=lambda: remove_timezone(datetime.now(timezone.utc))
    )

    order: Optional["Order"] = Relationship(back_populates="order_items")
    product: Optional["Product"] = Relationship(back_populates="order_items")


# ---------------- Reviews ---------------------#
class ReviewBase(SQLModel):
    rating: int = Field(ge=1, le=5)
    comment: Optional[str] = None


class Review(ReviewBase, table=True):
    review_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.user_id", index=True)
    product_id: uuid.UUID = Field(foreign_key="product.product_id", index=True)
    created_at: datetime = Field(
        default_factory=lambda: remove_timezone(datetime.now(timezone.utc))
    )
    updated_at: datetime = Field(
        default_factory=lambda: remove_timezone(datetime.now(timezone.utc))
    )

    user: Optional["User"] = Relationship(back_populates="reviews")
    product: Optional["Product"] = Relationship(back_populates="reviews")


# ---------------- Cart ---------------------#
class Cart(SQLModel, table=True):
    cart_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.user_id", index=True)
    created_at: datetime = Field(
        default_factory=lambda: remove_timezone(datetime.now(timezone.utc))
    )
    updated_at: datetime = Field(
        default_factory=lambda: remove_timezone(datetime.now(timezone.utc))
    )

    user: Optional["User"] = Relationship(back_populates="cart")
    cart_items: List["CartItem"] = Relationship(
        back_populates="cart", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


# ---------------- CartItem ---------------------#
class CartItem(SQLModel, table=True):
    cart_item_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    cart_id: uuid.UUID = Field(foreign_key="cart.cart_id", index=True)
    product_id: uuid.UUID = Field(foreign_key="product.product_id", index=True)
    quantity: int = Field(default=1, ge=1)
    updated_at: datetime = Field(
        default_factory=lambda: remove_timezone(datetime.now(timezone.utc))
    )

    cart: Optional["Cart"] = Relationship(back_populates="cart_items")
    product: Optional["Product"] = Relationship(back_populates="cart_items")


# ---------------- Payments ---------------------#
class PaymentStatus(str, Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"


class PaymentBase(SQLModel):
    status: PaymentStatus = Field(default=PaymentStatus.pending)
    amount: float = Field(ge=0)
    transaction_id: Optional[str] = None


class Payment(PaymentBase, table=True):
    payment_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    order_id: uuid.UUID = Field(foreign_key="order.order_id", index=True)
    created_at: datetime = Field(
        default_factory=lambda: remove_timezone(datetime.now(timezone.utc))
    )
    updated_at: datetime = Field(
        default_factory=lambda: remove_timezone(datetime.now(timezone.utc))
    )

    order: Optional["Order"] = Relationship(back_populates="payment")


# ------------------ Categories------------------------#
class CategoryBase(SQLModel):
    category_name: str
    parent_category_id: Optional[uuid.UUID] = Field(
        foreign_key="category.category_id", default=None, nullable=True
    )


class Category(CategoryBase, table=True):
    category_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    image_url: Optional[str] = None

    created_at: datetime = Field(
        default_factory=lambda: remove_timezone(datetime.now(timezone.utc))
    )
    updated_at: datetime = Field(
        default_factory=lambda: remove_timezone(datetime.now(timezone.utc))
    )
    name_tsv: str = Field(sa_column=Column(TSVECTOR, index=True))

    products: List["Product"] = Relationship(
        back_populates="categories", link_model=ProductCategory
    )
