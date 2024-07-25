import os
import shutil
from typing import Annotated, List
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import Date, cast, func
from email_utiliity import send_email



from sqlalchemy.orm import Session
from auth import create_access_token, get_current_user, verify_password, pwd_context
from db import SessionLocal, Product, Customer, Sale
from pydantic_model import ProductRequest, ProductResponse, UserCreate, SaleRequest, SaleResponse, loginRequest, Tags

import sentry_sdk


sentry_sdk.init(
    dsn="https://9f21ea0acc3e9b24f0f3528d921b6e4d@o4507324307668992.ingest.us.sentry.io/4507384183193600",
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
        # "http://localhost:3000",
        # "http://localhost:5173",
        # "http://64.225.71.67",
        # "http://161.35.148.255:3000",
        # "http://127.0.0.1/:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure directories
STATIC_DIRECTORY = "default/path/to/static/files"
UPLOAD_DIRECTORY = "default/path/to/uploads"

os.makedirs(STATIC_DIRECTORY, exist_ok=True)
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIRECTORY), name="static")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



@app.get("/sentry-debug")
async def trigger_error():
    division_by_zero = 1 / 0




@app.post("/register", tags=[Tags.UserCreate.value])
async def create_user(add_user: UserCreate, db: Session = Depends(get_db)):
    hashed_password = pwd_context.hash(add_user.user_password)
    new_customer = Customer(
        username=add_user.username,
        user_email=add_user.user_email,
        user_password=hashed_password,
        phone_no=add_user.phone_no
    )
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)

    # Send a welcome email
    send_email(
        to_email=new_customer.user_email,
        subject="Welcome to Our Service",
        body=f"Hi {new_customer.username},\n\nThank you for registering with us!"
    )
    
    return new_customer




@app.post('/login', tags=[Tags.LOGIN.value])
def login_user(login_request: loginRequest, db: Session = Depends(get_db)):
    user = db.query(Customer).filter(Customer.username == login_request.username).first()
    if not user or not verify_password(login_request.user_password, user.user_password):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Credentials"
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}




@app.post('/products', response_model=ProductResponse, tags=[Tags.PRODUCTS.value, Tags.PRODUCT_IMAGE.value])
async def add_product(
    user: Annotated[dict, Depends(get_current_user)],
    product: ProductRequest = Depends(),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        db_product = Product(
            name=product.name,
            price=product.price,
            stock_quantity=product.stock_quantity,
            cost=product.cost,
            user_id=user.get("id")
        )
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        product_id = db_product.id

        file_extension = os.path.splitext(file.filename)[1]
        new_filename = f"{product_id}{file_extension}"

        file_path = os.path.join(UPLOAD_DIRECTORY, new_filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        img_url = f"/uploads/{new_filename}"
        db_product.image_url = img_url
        db.commit()
        db.refresh(db_product)

        return ProductResponse.from_orm(db_product)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail="An error occurred while adding the product."
        )




@app.get('/products', response_model=List[ProductResponse], tags=[Tags.PRODUCTS.value])
def fetch_products(request: Request, db: Session = Depends(get_db)):
    try:
        products = db.query(Product).all()
        base_url = str(request.base_url)
        products_with_images = [
            ProductResponse(
                id=product.id,
                name=product.name,
                stock_quantity=product.stock_quantity,
                price=product.price,
                image_url=f"{base_url.rstrip('/')}/images/{product.id}.jpg",
                cost=product.cost,
                user_id=product.user_id
            ) for product in products
        ]
        return products_with_images
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))



@app.get('/products/{id}', response_model=ProductResponse, tags=[Tags.PRODUCTS.value])
def fetch_single_product(id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product does not exist")
    return product




@app.put('/purchase/{product_id}', tags=[Tags.PURCHASE.value])
def purchase_product(product_id: int, quantity: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product.stock_quantity < quantity:
        raise HTTPException(
            status_code=400, detail="Not enough stock available"
        )
    product.stock_quantity -= quantity
    db.commit()
    return {"message": "Purchase successful"}




@app.post('/sales', tags=[Tags.PURCHASE.value])
def add_sale(sale: SaleRequest, db: Session = Depends(get_db)):
    try:
        new_sale = Sale(
            pid=sale.pid,
            total_amount=sale.total_amount,
            created_at=sale.created_at,
            id=sale.id
        )
        db.add(new_sale)
        db.commit()
        db.refresh(new_sale)
        return new_sale
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/sales', response_model=List[SaleResponse], tags=[Tags.PURCHASE.value])
def fetch_sales(db: Session = Depends(get_db)):
    sales = db.query(Sale).all()
    return sales

@app.get('/dashboard')
def dashboard(db: Session = Depends(get_db)):
    sales_per_day = db.query(
        cast(func.date_trunc('day', Sale.created_at), Date).label('date'),
        func.sum(Sale.quantity * Product.price).label('total_sales')
    ).join(Product).group_by(
        cast(func.date_trunc('day', Sale.created_at), Date)
    ).all()

    sales_data = [{'date': str(day), 'total_sales': sales} for day, sales in sales_per_day]

    sales_per_product = db.query(
        Product.name,
        func.sum(Sale.quantity * Product.price).label('sales_product')
    ).join(Sale).group_by(
        Product.name
    ).all()

    salesproduct_data = [{'name': name, 'sales_product': sales_product} for name, sales_product in sales_per_product]

    return {'sales_data': sales_data, 'salesproduct_data': salesproduct_data}

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)
