from fastapi import FastAPI,Depends,HTTPException,UploadFile,File,Request,status
from sqlalchemy import Date, cast, func
from starlette.responses import FileResponse
from db import Base,engine,SessionLocal,Product,Customer,Sale
from sqlalchemy.orm import Session
from pydantic_model import ProductRequest,ProductResponse,UserResponse,UserCreate,Tags,\
UserLogin,ImageResponse,SaleRequest,SaleResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os,base64,tempfile
from pathlib import Path
from typing import Annotated
from passlib.context import CryptContext
from auth import create_access_token,get_current_user
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import StreamingResponse




app = FastAPI()

origins = ["http://localhost:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Define STATIC_DIRECTORY
STATIC_DIRECTORY = os.getenv("STATIC_DIRECTORY", "default/path/to/static/files")

# Ensure the static files directory exists
if not os.path.exists(STATIC_DIRECTORY):
    os.makedirs(STATIC_DIRECTORY)

# Mount the static files directory
app.mount("/static", StaticFiles(directory=STATIC_DIRECTORY), name="static")

# Define UPLOAD_DIRECTORY
UPLOAD_DIRECTORY = os.getenv("UPLOAD_DIRECTORY", "default/path/to/uploads")

# Ensure the uploads directory exists
if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

@app.post("/register" ,tags=[Tags.UserCreate.value])
async def create_user(add_user: UserCreate,  db: Session = Depends(get_db)):

    hashedpasword=pwd_context.hash(add_user.user_password)

    db = SessionLocal()
    new_customer = Customer(
        user_name = add_user.user_name,
        user_email = add_user.user_email,
        user_password =hashedpasword,
        user_contact=add_user.user_contact
        )
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    return new_customer

@app.post("/upload/", tags=[Tags.PRODUCT_IMAGE.value])
async def upload_image(file: UploadFile = File(...)):
    with open(os.path.join(UPLOAD_DIRECTORY, file.filename), "wb") as buffer:
        buffer.write(await file.read())

    return {"filename": file.filename}



@app.get("/images" , tags=[Tags.PRODUCT_IMAGE.value])
async def get_images(request: Request):

    try:
        image_files = [file for file in os.listdir(UPLOAD_DIRECTORY) if file.endswith(('.jpg', '.png', '.jpeg'))]
        print("first........",image_files)
        base_url = str(request.base_url)
        print('second',base_url)
        image_urls = [f"{base_url.rstrip('/')}/images/{file}" for file in image_files]
        print('third.....l',image_urls)
        return image_urls

    except Exception as e:
      
        print(f"Error fetching images: {e}")
      
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get("/images/{filename}",tags=[Tags.PRODUCT_IMAGE.value])
async def get_image(filename: str):
    # Check if the image exists
    image_path = os.path.join(UPLOAD_DIRECTORY, filename)
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image not found")

    # Return the image file
    return StreamingResponse(open(image_path, "rb"), media_type="image/jpeg")


#Products...(post ,get and put)
@app.post('/products', tags=[Tags.PRODUCTS.value])
def add_product(product: ProductRequest, db: Session = Depends(get_db)):
    db_product = Product(name=product.name, price=product.price, stock_quantity=product.stock_quantity, cost=product.cost)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

    
@app.get('/products', response_model=list[ProductResponse], tags=[Tags.PRODUCTS.value])
def fetch_products(request: Request,db: Session = Depends(get_db)):
    try:
        products = db.query(Product).all()
        print("products.......",products)
        products_with_images = []
        for product in products:
            image_filename = f"product_{product.id}.jpg" 
            base_url = str(request.base_url)
            image_url =  f"{base_url.rstrip('/')}/images/{image_filename}"
            print("kwanzaaaaa ...............",image_url)
            products_with_images.append(ProductResponse(
                id=product.id,
                product_name=product.product_name,
                stock_quantity=product.stock_quantity,
                price=product.price,
                image_url=image_url
            ))
        return products_with_images
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# fetch by product id
@app.get('/products/{id}', response_model=ProductResponse ,tags=[Tags.PRODUCTS.value])
def fetch_single_products(id: int, db: Session = Depends(get_db)):
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
        raise HTTPException(status_code=400, detail="Not enough stock available")
    product.stock_quantity -= quantity
    db.commit()
    return {"message": "Purchase successful"}



#sales get and post
@app.post('/sales')
def add_sale(sale: SaleRequest, db: Session = Depends(get_db)):
    try:
        new_sale=Sale(pid=sale.pid,quantity=sale.quantity,created_at=sale.created_at,customer_id=sale.customer_id)
        db.add(new_sale)
        db.commit()
        db.refresh(new_sale)
        return new_sale

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get('/sales',response_model= list[SaleResponse])
def fetch_sales(db: Session = Depends(get_db)):
    sales=db.query(Sale).all()
    return sales


#password hashing using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


@app.post("/register", tags=[Tags.UserCreate.value])
async def create_customer(add_customer: UserCreate, db: Session = Depends(get_db)):
    hashed_password = pwd_context.hash(add_customer.password)
    new_customer = Customer(
        name=add_customer.name,
        email=add_customer.email,
        user_password=hashed_password,
        phone_no=add_customer.phone_no
    )
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    return new_customer



#login
@app.post('/login' ,tags=[Tags.LOGIN.value])
def login_user(login_details: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)):

    user=db.query(Customer).filter(Customer.user_name==login_details.username).first()
    print("loginn.......",login_details)
    if not user:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail =f"Invalid Credentials")
    if not verify_password(login_details.password, user.password):
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail =f"Invalid Credentials")

    
    access_token = create_access_token(data={"sub": user.user_name})
    return {"access_token":access_token, "token_type":"bearer"}

@app.get('/dashboard')
def dashboard(  db: Session = Depends(get_db)):
    # customer = Customer.query.filter_by(user_name=user_name).first()
    # if not customer:
    #     return {"message": "User not found"}, 404

    sales_per_day = db.query(
        cast(func.date_trunc('day', Sale.created_at), Date).label('date'),
        # calculate the total number of sales per day
        func.sum(Sale.quantity * Product.price).label('total_sales')
    ).join(Product).group_by(
        cast(func.date_trunc('day', Sale.created_at), Date)
    

    ).all()

    #  to JSON format
    sales_data = [{'date': str(day), 'total_sales': sales}
                  for day, sales in sales_per_day]
    #  sales per product
    sales_per_product = db.query(
        Product.product_name,
        func.sum(Sale.quantity*Product.product_price).label('sales_product')
    ).join(Sale).group_by(
        Product.product_name
    ).all()
    
    # to JSON format
    salesproduct_data = [{'name': name, 'sales_product': sales_product}
                         for name, sales_product in sales_per_product]

    return {'sales_data': sales_data, 'salesproduct_data': salesproduct_data}