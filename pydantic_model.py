from pydantic import BaseModel
from datetime import datetime
from enum import Enum
from typing import Optional

class Tags(Enum):
    PRODUCTS= "product"
    UserCreate = "Customers"
    PRODUCT_IMAGE = "product_image"
    LOGIN = "UserLogin"
    PURCHASE = "purchase"

class UserLogin(BaseModel):
    username: str
    password: str

class TokenData(BaseModel):
    username:  Optional[str] =  None


class ProductRequest(BaseModel):
    product_name: str
    price: float
    stock_quantity: int
    cost : float



class ProductResponse(BaseModel):
    id: int
    product_name: str
    price: float
    stock_quantity: int
    image_url : str

   
class SaleRequest(BaseModel):
    total_amount: float
    created_at: Optional[datetime]
    customer_id: int

class SaleResponse(SaleRequest):
    id: int
    

class UserCreate(BaseModel):
    user_name: str
    user_password: str
    user_email: str
    phone_no: str

class UserResponse(BaseModel):
    id: int
    user_name: str
    user_email: str
    user_contact: str



class ImageResponse(BaseModel):
    filename: str
    content_type: str

    # class Config:
    #     orm_mode = True