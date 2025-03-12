from fastapi import APIRouter


Cart_router = APIRouter(prefix="/cart", tags=["Cart"])


@Cart_router.get("/")
async def get_cart_items():
    pass


@Cart_router.post("/add")
async def add_to_cart():
    pass


@Cart_router.delete("/{item_id}")
async def remove_from_cart():
    pass
