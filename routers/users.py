# Tarea
import sys
sys.path.append("..")

from fastapi import APIRouter, Depends, HTTPException, Request, Form
from database import engine, SessionLocal
from sqlalchemy.orm import Session
import models
from pydantic import BaseModel
from .auth import authenticate_user, get_current_user, logout, verify_password, get_password_hash

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from starlette.responses import RedirectResponse
from starlette import status

router = APIRouter(
    prefix="/users", 
    tags=["Users"],  
    responses={404: {"description": "User Not Found"}}
)

models.Base.metadata.create_all(bind=engine)

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

templates = Jinja2Templates(directory="templates")        

@router.get("/", response_class=HTMLResponse)
async def user_info(request: Request, db: Session = Depends(get_db)):

    # Verifico que el token JWT esté (Usuario logueado e info)
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    
    user_data = db.query(models.Users).filter(models.Users.id == user.get("id")).first()

    return templates.TemplateResponse("user.html", {"request": request, "user": user_data})

@router.post("/", response_class=HTMLResponse)    
async def change_password(  request: Request, 
                            password: str = Form(...),
                            newpassword: str = Form(...),
                            newpassword2: str = Form(...),
                            db: Session = Depends(get_db)):

    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    user_data = db.query(models.Users).filter(models.Users.id == user.get("id")).first()

    # Verifico el password actual
    validation1 = authenticate_user(user.get("username"), password, db)
    # Verifico que coincida el password nuevo
    validation2 = True if newpassword == newpassword2 else False

    if validation1 is False or validation2 is False:
        msg = "El password no coincide"
        return templates.TemplateResponse("user.html", {"request":request, "msg": msg, "user": user_data})

    user_data.hashed_password = get_password_hash(newpassword)

    db.add(user_data)
    db.commit()

    msg = "Contraseña Actualizada"
    response = templates.TemplateResponse("login.html", {"request": request, "msg": msg})
    response.delete_cookie(key="access_token")
    return response

# # Devuelve un usuario por id por parámetro
# @router.get("/{user_id}")
# async def get_user(user_id: int, db: Session = Depends(get_db)):
#     user_model = db.query(models.Users).filter(models.Users.id == user_id).first()
#     if user_model is not None:
#         return user_model
#     else:
#         raise HTTPException(status_code=404, detail="User Not Found")

# # Devuelve un usuario por id por query
# @router.get("/id/")
# async def get_user(user_id: str, db: Session = Depends(get_db)):
#     if user_id:
#         user_model = db.query(models.Users).filter(models.Users.id == user_id).first()
#         if user_model is not None:
#             return user_model
#         else:
#             raise HTTPException(status_code=404, detail="User Not Found")

# # Ahora lo mismo pero usando autenticación

# # Creo una clase para el modelo de usuario cuando quiero cambiar el password
# class UserVerification(BaseModel):
#     username: str
#     password: str
#     new_password: str

# # Método para cambiar el password, verifica que el usuario esté autenticado
# @router.put("/password")
# async def change_password(  user_verification: UserVerification, 
#                             user: dict = Depends(get_current_user),
#                             db: Session = Depends(get_db)
#                         ):
#     if user is None:
#         raise get_user_exception()

#     user_model = db.query(models.Users).filter(models.Users.id == user.get('id')).first()

#     # Uso los métodos de auth para verificar el usuario
#     if user_model is not None:
#         if user_verification.username == user_model.username and verify_password(
#             user_verification.password, 
#             user_model.hashed_password):

#             # Asigno el nuevo password
#             user_model.hashed_password = get_password_hash(user_verification.new_password)
#             db.add(user_model)
#             db.commit()
#             return 'Successful'
#     return 'Invalid User Request'

# # Método para eliminar el propio usuario
# @router.delete("/")
# async def delete_user(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
#     if user is None:
#         raise get_user_exception()

#     user_model = db.query(models.Users).filter(models.Users.id == user.get("id")).first()

#     if user_model is None:
#         return "Invalid User Request"

#     db.query(models.Users).filter(models.Users.id == user.get("id")).delete()

#     db.commit()

#     return "Delete Successful"



