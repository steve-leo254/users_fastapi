from pydantic import BaseModel
from datetime import datetime

class UserOut(BaseModel):
    username: str
    email: str

class UserCreate(UserOut):
    password: str



class UserLogin(BaseModel):
    username: str
    password: str


class CustomerBase(BaseModel):
    name: str
    phone_no: str
    email: str

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(CustomerBase):
    name: str 
    phone_no: str = None
    email: str = None

class Customer(CustomerBase):
    id: int


class SaleBase(BaseModel):
    total_amount: float
    created_at: datetime

class SaleCreate(SaleBase):
    pass

class SaleUpdate(SaleBase):
    total_amount: float 

class Sale(SaleBase):
    id: int


class ProductBase(BaseModel):
    name: str
    cost: float
    price:float
    stock_quantity:int


class ProductUpdate(BaseModel):
    name: str | None = None
    cost: float | None = None
    price: float | None = None
    stock_quantity: int | None = None

class ProductUpdateOut(ProductUpdate):
    id: int


class ProductCreate(ProductBase):
    pass


class Product(ProductBase):
    id: int

    class Config:
        orm_mode = True
