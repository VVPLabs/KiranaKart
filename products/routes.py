from fastapi import APIRouter


Product_router = APIRouter(prefix="/products", tags=["Products"])


@Product_router.get("/")
async def all_products():
    pass

@Product_router.post("/")
async def add_product():
    pass



@Product_router.get("/{product_id}")
async def show_product():
    pass




@Product_router.patch("/{Product_id}")
async def update_product():
    pass


@Product_router.delete("/{Product_id}")
async def delete_product():
    pass
