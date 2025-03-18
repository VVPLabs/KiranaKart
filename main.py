from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.utils import get_openapi

from products.routes import Product_router
from auth.routes import Auth_router
from cart.routes import Cart_router
from categories.routes import Category_router
from orders.routes import Order_router
from payment.routes import Payment_router
from review.routes import Review_router
from user.routes import User_router


version = "v1"


app = FastAPI(
    title="KiranaKart",
    description=" E-commerce practice project",
    version=version,
    openapi_url="/openapi.json"
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        openapi_version="3.0.3",  # Ensuring OpenAPI 3.0.3
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi


app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(Product_router)
app.include_router(Auth_router)
app.include_router(Cart_router)
app.include_router(Category_router)
app.include_router(Order_router)
app.include_router(Payment_router)
app.include_router(Review_router)
app.include_router(User_router)


@app.get("/")
def root():
    return {"message": "Welcome to FastAPI E-Commerce API"}
