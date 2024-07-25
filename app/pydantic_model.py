from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum
from typing import Optional

class Tags(Enum):
    PRODUCTS = "product"
    UserCreate = "Customers"
    PRODUCT_IMAGE = "product_image"
    LOGIN = "login"
    PURCHASE = "purchase"

class TokenData(BaseModel):
    user_id: Optional[int] = None
    username: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class loginRequest(BaseModel):
    username: str
    user_password: str

class ProductRequest(BaseModel):
    name: str = Field(..., example="Sample Product")
    price: float = Field(..., example=19.99)
    stock_quantity: int = Field(..., example=100)
    cost: float = Field(..., example=10.00)

class ProductResponse(BaseModel):
    id: int
    name: str
    price: float
    stock_quantity: int
    cost: float
    image_url: str
    user_id: str

    class Config:
        orm_mode = True

class SaleRequest(BaseModel):
    pid: int
    total_amount: float
    created_at: Optional[datetime]
    customer_id: int

class SaleResponse(SaleRequest):
    id: int

    class Config:
        orm_mode = True

class UserCreate(BaseModel):
    username: str
    user_password: str
    user_email: str
    phone_no: str

class UserResponse(BaseModel):
    id: int
    username: str
    user_email: str
    phone_no: str

    class Config:
        orm_mode = True

class ImageResponse(BaseModel):
    filename: str
    content_type: str
