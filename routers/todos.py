import sys
sys.path.append("..")

from typing import Optional
from fastapi import Depends, HTTPException, APIRouter, Request, Form
import models               # Importo los modelos
from database import engine, SessionLocal # Setup de la BD
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from .auth import get_current_user

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from starlette.responses import RedirectResponse
from starlette import status

# router = APIRouter()
router = APIRouter(
    prefix="/todos", # Agrega este prefijo a las url de todos los path de esta api
    tags=["ToDo's"],  # Permite que se visualice este nombre separado en la documentación de Swagger
    responses={404: {"description": "Not Found"}} # Respuesta predefinida en caso de que no exista manejo del error
)

# Creo la base de datos con los modelos definidos
models.Base.metadata.create_all(bind=engine)

# Agrego los templates de Jinja2
templates = Jinja2Templates(directory="templates")

# Funcion auxiliar para crear una sesion con la base de datos local
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

@router.get("/", response_class=HTMLResponse)
async def read_all_by_user(request: Request, db: Session = Depends(get_db)):
    
    user = await get_current_user(request)  # Verificamos que el request incluya el cookie con el token JWT
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND) # Si no, lo mandamos al login

    todos = db.query(models.Todos).filter(models.Todos.owner_id == user.get("id")).all() # Verificamos qué usuario lo está solicitando

    return templates.TemplateResponse("home.html", {"request": request, "todos": todos, "user": user})

@router.get("/add-todo", response_class=HTMLResponse)
async def add_new_todo(request: Request):

    user = await get_current_user(request)  # Verificamos que el request incluya el cookie con el token JWT
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND) # Si no, lo mandamos al login

    return templates.TemplateResponse("add-todo.html", {"request": request, "user": user})    

@router.post("/add-todo", response_class=HTMLResponse)
async def create_todo(
    request: Request, 
    title: str = Form(...), 
    description: str = Form(...),
    priority: int = Form(...),
    db: Session = Depends(get_db)):

    user = await get_current_user(request)  # Verificamos que el request incluya el cookie con el token JWT
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND) # Si no, lo mandamos al login
    
    todo_model = models.Todos()
    todo_model.title = title
    todo_model.description = description
    todo_model.priority = priority
    todo_model.complete = False
    todo_model.owner_id = user.get("id")

    db.add(todo_model)
    db.commit()

    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)

@router.get("/edit-todo/{todo_id}", response_class=HTMLResponse)
async def edit_todo(request: Request, todo_id: int, db: Session = Depends(get_db)):
    
    user = await get_current_user(request)  # Verificamos que el request incluya el cookie con el token JWT
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND) # Si no, lo mandamos al login

    todo = db.query(models.Todos).filter(models.Todos.id == todo_id).filter(models.Todos.owner_id == user.get("id")).first()

    return templates.TemplateResponse("edit-todo.html", {"request": request, "todo": todo, "user": user})

# Ver que se pone método POST en el form de edit-todo.html
@router.post("/edit-todo/{todo_id}", response_class=HTMLResponse)
async def edit_todo_commit(
    request: Request, 
    todo_id: int,
    title: str = Form(...), 
    description: str = Form(...),
    priority: int = Form(...),
    db: Session = Depends(get_db)):

    user = await get_current_user(request)  # Verificamos que el request incluya el cookie con el token JWT
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND) # Si no, lo mandamos al login

    todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id).filter(models.Todos.owner_id == user.get("id")).first()

    todo_model.title = title
    todo_model.description = description
    todo_model.priority = priority

    db.add(todo_model)
    db.commit()

    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)  

# Si esto fuera sólo la API, podemos usar el método delete para eliminarlo, pero como es una aplicación full-stack,
# Usamos un get para redirigir
@router.get("/delete/{todo_id}")
async def delete_todo(request: Request, todo_id: int, db: Session = Depends(get_db)):

    user = await get_current_user(request)  # Verificamos que el request incluya el cookie con el token JWT
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND) # Si no, lo mandamos al login

    todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id).filter(models.Todos.owner_id == user.get("id")).first()

    if todo_model is None:
        return RedirectResponse("/todos",status_code=status.HTTP_302_FOUND) 

    db.query(models.Todos).filter(models.Todos.id == todo_id).filter(models.Todos.owner_id == user.get("id")).delete()
    db.commit()

    return RedirectResponse(url="/todos",status_code=status.HTTP_302_FOUND)

@router.get("/complete/{todo_id}", response_class=HTMLResponse)
async def todo_complete(request: Request, todo_id: int, db: Session = Depends(get_db)):
    
    user = await get_current_user(request)  # Verificamos que el request incluya el cookie con el token JWT
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND) # Si no, lo mandamos al login

    todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id).filter(models.Todos.owner_id == user.get("id")).first()

    # Invierto el estado y cambio en el HTML
    todo_model.complete ^= True

    db.add(todo_model)
    db.commit()

    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)