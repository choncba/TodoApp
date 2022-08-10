import os

from sqlite3 import connect
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Para usar la BD local SQLite3
# SQLALCHEMY_DATABASE_URL = "sqlite:///./todos.db"  
# Para usar Postgres del Add-on de Heroku
SQLALCHEMY_DATABASE_URL = os.environ.get("DATABASE_URL")

# Corrijo la URL de Heroku para que lo tome bien
if SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

