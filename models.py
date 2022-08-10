from sqlalchemy import Boolean, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship # Permite relacionar valores de una tabla en otra tabla
from database import Base # Lo importo del archivo database

# Creo los modelos de las tablas de la base de datos para usuarios y las tareas

# Modelo para usuarios
class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    # Relacionamos la tabla Todos
    todos = relationship("Todos", back_populates="owner")

# Modelo para todos
class Todos(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    complete = Column(Boolean, default=False)
    
    # Agregamos la columna para el id de usuario
    owner_id = Column(Integer, ForeignKey("users.id"))
    # Y relacionamos con la tabla Users
    owner = relationship("Users", back_populates="todos")
