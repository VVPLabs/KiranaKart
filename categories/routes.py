from fastapi import APIRouter


Category_router = APIRouter(prefix="/categories", tags=["Categories"])


@Category_router.get("/")
async def get_all_categories():
    pass


@Category_router.post("/")
async def create_category():
    pass
