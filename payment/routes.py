from fastapi import APIRouter


Payment_router = APIRouter(prefix="/payment", tags=["Payment"])


@Payment_router.post("/process")
async def process_payment():
    pass
