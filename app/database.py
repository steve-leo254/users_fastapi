from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from typing import Annotated
from fastapi import Depends
from sqlalchemy.orm import Session



password = 'leo.steve'
URL_DATABASE = 'postgresql://postgres:leo.steve@172.17.0.1:5432/myduka_app'
engine =create_engine(URL_DATABASE)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Corrected usage of Depends for database session
db_dependency = Depends(get_db)