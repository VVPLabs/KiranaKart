from fastapi import APIRouter


Order_router = APIRouter(prefix="/orders", tags=["Orders"])


@Order_router.get("/")
async def get_orders():
    pass


@Order_router.post("/")
async def create_order():
    pass


@Order_router.get("/{order_id}")
async def get_order():
    pass
