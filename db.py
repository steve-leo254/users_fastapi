from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, Session
from datetime import datetime, timezone
from werkzeug.security import check_password_hash

SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:leo.steve@localhost:5432/sale_system_api'
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)




Base = declarative_base()


from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from werkzeug.security import generate_password_hash
import datetime

Base = declarative_base()

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    stock_quantity = Column(Integer, default=0)
    user_id = Column(Integer, ForeignKey('customers.id'))  # Corrected ForeignKey reference

class Sale(Base):
    __tablename__ = 'sales'
    id = Column(Integer, primary_key=True)
    total_amount = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    customer = relationship('Customer', backref='sales')  # Changed 'sale' to 'sales' for consistency

class Customer(Base):
    __tablename__ = "customers"  
    id = Column(Integer, primary_key=True)
    user_name = Column(String, nullable=False)
    user_password = Column(String(255), nullable=False)  # Renamed for clarity
    hashed_password = Column(String(255))  # Store hashed passwords
    phone_no = Column(String, nullable=False)
    email = Column(String, nullable=False)  # Renamed for clarity

    def set_password(self, password):
        """Create hashed password."""
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        """Check hashed password."""
        return check_password_hash(self.hashed_password, password)

Base.metadata.create_all(bind=engine)