from sqlite3 import connect
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import pymysql

MYSQL_URL = "ae-media-mysql.cb0wbmrrr5hp.us-east-1.rds.amazonaws.com"
MYSQL_USER = "u518765"
MYSQL_PASSWORD = "Chon082022"
MYSQL_DB_NAME = "todoapp"

SQLALCHEMY_DATABASE_URL =   "mysql+pymysql://" + \
                            MYSQL_USER + \
                            ":" + \
                            MYSQL_PASSWORD + \
                            "@" + \
                            MYSQL_URL + \
                            "/" + \
                            MYSQL_DB_NAME

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

