from sqlite3 import connect
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Para usar la BD local SQLite3
# SQLALCHEMY_DATABASE_URL = "sqlite:///./todos.db"  
# Para usar Postgres del Add-on de Heroku
SQLALCHEMY_DATABASE_URL = "postgres://ebtnxpyyomksvd:2c1194ffbf15a921dc4b535d70abe517d96cbe01b571c0bbba8425bfc2ec9f1d@ec2-34-193-44-192.compute-1.amazonaws.com:5432/d2120uf9k2ljha"


engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

