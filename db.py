from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, Session
from datetime import datetime, timezone

SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:leo.steve@localhost:5432/sale_system_api'
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    products = relationship("Product", back_populates="user")

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    cost = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    stock_quantity = Column(Integer, default=0)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    user = relationship("User", back_populates="products")

class Sale(Base):
    __tablename__ = 'sale'
    id = Column(Integer, primary_key=True)
    total_amount = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class Customers(Base):
    __tablename__ = "customers"  # Fixed typo here
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    phone_no = Column(String, nullable=False)
    email = Column(String, nullable=False)

Base.metadata.create_all(bind=engine)