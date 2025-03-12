from fastapi import FastAPI

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
)



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
