from fastapi import APIRouter


Review_router = APIRouter(prefix="/reviews", tags=["Reviews"])


@Review_router.get("/{product_id}")
async def get_reviews():
    pass


@Review_router.post("/{product_id}")
async def add_review():
    pass
