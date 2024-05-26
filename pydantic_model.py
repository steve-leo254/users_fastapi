from pydantic import BaseModel
from datetime import datetime
from enum import Enum
from typing import Optional

class Tags(Enum):
    PRODUCTS= "product"
    UserCreate = "Customers"
    PRODUCT_IMAGE = "product_image"
    LOGIN = "login"
    PURCHASE = "purchase"
    # loginUser = "loginRequest"


class UserLogin(BaseModel):
    username: str
    password: str

class TokenData(BaseModel):
    username:  Optional[str] =  None



class login(BaseModel):
    user_name : str
    user_password : str


class loginRequest(BaseModel):
    user_name : str
    user_password : str


class ProductRequest(BaseModel):
    name: str
    price: float
    stock_quantity: int
    cost : float



class ProductResponse(BaseModel):
    id: int
    name: str
    price: float
    stock_quantity: int
    image_url : str
    cost :float

   
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