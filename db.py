from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# Database URL
SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:leo.steve@localhost:5432/sale_system_api'

# Create engine and session
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for declarative models
Base = declarative_base()

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    cost = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    stock_quantity = Column(Integer, default=0, nullable=False)
    image_url = Column(String)
    user_id = Column(Integer, ForeignKey('customers.id'), nullable=False)

    customer = relationship('Customer', back_populates='products')



class Sale(Base):
    __tablename__ = 'sales'
    id = Column(Integer, primary_key=True)
    total_amount = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)

    customer = relationship('Customer', back_populates='sales')

class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True)
    user_name = Column(String, nullable=False)
    user_password = Column(String(255), nullable=False)
    phone_no = Column(String, nullable=False)
    user_email = Column(String, nullable=False)

    # Relationships
    products = relationship('Product', back_populates='customer')
    sales = relationship('Sale', back_populates='customer')

# Create all tables
Base.metadata.create_all(bind=engine)
