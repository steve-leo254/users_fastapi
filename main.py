from fastapi import FastAPI,HTTPException,Depends
from datetime import timedelta
from db import SessionLocal,User,Product
from pydatic_model import UserCreate, UserLogin, ProductCreate, UserOut, ProductBase, ProductUpdate, ProductUpdateOut
from fastapi.middleware.cors import CORSMiddleware
from auth import pwd_context,authenticate_user,create_access_token,ACCESS_TOKEN_EXPIRE_MINUTES,get_current_user

app=FastAPI()

origins=[
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)
db = SessionLocal()


@app.post("/register" ,response_model=UserOut)
def create_user(user: UserCreate):
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(
            status_code=400, detail="Username already registered")
    password = pwd_context.hash(user.password)
    db_user = User(username=user.username,email=user.email, password=password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    db.close()
    return db_user


@app.post("/login")
def login(user: UserLogin):
    db_user = authenticate_user(user.username, user.password)
    if not db_user:
        raise HTTPException(
            status_code=401, detail="Incorrect username or password")
    access_token = create_access_token(
        data={"sub": db_user.username}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    print(access_token)
    return {"access_token": access_token, "token_type": "bearer"}





@app.get("/products")
def get_products(current_user: User = Depends(get_current_user)):
    products = db.query(Product).filter(
        Product.user_id == current_user.id).all()
    db.close()
    return products


@app.post("/products")
def create_product(product: ProductCreate, current_user: User = Depends(get_current_user)):
    db_product = Product(name=product.name,price=product,quantity=product.quantity,user id=current_user.id)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    db.close()
    return db_product

@app.put("/products/{pid}")
async def update_item(pid: int, product: ProductUpdate, response_model=Product):
    prod=db.query(Product).filter(Product.id==pid).first()
    if not prod :
        raise HTTPException(status_code=404,detail="product does not exist")

    if not prod.name == product.name and product.name != None:
        prod.name = product.name

    if not prod.cost == product.cost and product.cost != None:
        prod.cost = product.cost
    
    if not prod.price == product.price and product.price != None:
        prod.price = product.price
    
    if not prod.stock_quantity == product.stock_quantity and product.stock_quantity != None:
        prod.stock_quantity = product.stock_quantity
    db.commit()

    prod = db.query(Product).filter(Product.id == pid).first()
    return prod

@app.get("/users")
def get_all_users():
    users = db.query(User).all()
    db.close()
    return users
