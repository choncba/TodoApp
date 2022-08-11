import sys
sys.path.append("..")

from fastapi import FastAPI, Depends, HTTPException, status, APIRouter, Request, Response, Form
from pydantic import BaseModel
from typing import Optional
import models
from passlib.context import CryptContext    # Para encriptar el password con bcrypt
from sqlalchemy.orm import Session          # Metodos de acceso a la BD
from database import SessionLocal, engine   # Local, modelo de DB
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer  # Form para login de usuarios de 0Auth2 y para JWT
from datetime import datetime, timedelta
from jose import jwt, JWTError    # Para trabajar con JWT

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from starlette.responses import RedirectResponse

# Definiciones para JWT
SECRRET_KEY = "chon2185"    # Esta secret key es la última posibilidad para desencriptar jwt
ALGORITHM = "HS256"         # Algoritmo de encripción

#app = FastAPI()
# Utilizo ahora routing
# router = APIRouter()
# Con prefijos
router = APIRouter(
    prefix="/auth", # Agrega este prefijo a las url de todos los path de esta api
    tags=["Auth"],  # Permite que se visualice este nombre separado en la documentación de Swagger
    responses={401: {"user": "Not Authorized"}} # Respuesta predefinida en caso de que no exista manejo del error
)

templates = Jinja2Templates(directory="templates")

# Variable de contexto de Bcrypt
bcrypt_context = CryptContext(schemes="bcrypt", deprecated="auto")

# Crea la base de datos, si no existe
models.Base.metadata.create_all(bind=engine)

# Variable de contexto de JWT
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="token")

class LoginForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.username: Optional[str] = None
        self.password: Optional[str] = None

    async def create_oauth_form(self):
        form = await self.request.form()
        self.username = form.get("email") # El formulario oauth requiere que este campo se llame email
        self.password = form.get("password")

# Conexión a la BD
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

# Devuelve el password encriptado
def get_password_hash(password):
    return bcrypt_context.hash(password)

# Verifica que el password en texto plano coincida con el password en hash
def verify_password(plain_password, hashed_password):
    return bcrypt_context.verify(plain_password, hashed_password)

# Verifica si el usuario/password es válido contra la BD, si lo es retorna el usuario
def authenticate_user(username: str, password: str, db):
    user = db.query(models.Users).filter(models.Users.username == username).first()
    if not user: 
        print("Usuario no encontrado")
        return False
    if not verify_password(password, user.hashed_password):
        print("Contraseña no coincide con el hash")
        return False
    return user

# Esta función genera el token de acceso con jwt, y carga el tiempo de expiración opcional
def create_access_token(username: str, user_id: int, expires_delta: Optional[timedelta] = None):
    
    encode = {"sub": username, "id": user_id}
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow + timedelta(minutes=15)
    
    encode.update({"exp": expire})  # Agrego el tiempo de expiración

    # Retorno el token JWT
    return jwt.encode(encode, SECRRET_KEY, algorithm=ALGORITHM)

async def get_current_user(request: Request):
    try:
        token = request.cookies.get("access_token") #### VERIFICAR que sea el mismo nombre de la cookie del browser
        if token is None:
            return None
        payload = jwt.decode(token, SECRRET_KEY, algorithms=[ALGORITHM])    # Decodifica el token JWT y devuelve un diccionario
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        if username is None or user_id is None:
            logout(request)
        return {"username": username, "id": user_id}
    except JWTError:
        raise HTTPException(status_code=404, detail="Not found")

@router.post("/token")
async def login_for_token(
    response: Response, 
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)):
    
    user = authenticate_user(form_data.username, form_data.password, db)
    
    if not user:
        return False
    
    token_expires = timedelta(minutes=60)
    token = create_access_token(user.username, user.id, expires_delta=token_expires)

    # Devuelvo una cookie con el token de acceso
    response.set_cookie(key="access_token", value=token, httponly=True)

    return True

@router.get("/", response_class=HTMLResponse)
async def authentication_page(request: Request):
    return templates.TemplateResponse("login.html",{"request":request} )

@router.post("/", response_class=HTMLResponse)
async def login(request: Request, db: Session = Depends(get_db)):

    try:
        form = LoginForm(request)
        await form.create_oauth_form()
        response = RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)

        validate_user_cookie = await login_for_token(response=response, form_data=form, db=db)

        if not validate_user_cookie:
            msg = "Usuario o contraseña Incorrecto"
            return templates.TemplateResponse("login.html", {"request":request, "msg": msg })
        
        return response
    
    except HTTPException:
        msg = "Error Desconocido"
        return templates.TemplateResponse("login.html", {"request":request, "msg": msg })

@router.get("/logout")
async def logout(request: Request):
    msg = "Logout"
    response = templates.TemplateResponse("login.html", {"request": request, "msg": msg})
    response.delete_cookie(key="access_token")
    return response

@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html",{"request":request} )

# API para crear un usuario desde el navegador
@router.post("/register", response_class=HTMLResponse)
async def register_user(request: Request,
                        email: str = Form(...),
                        username: str = Form(...),
                        firstname: str = Form(...),
                        lastname: str = Form(...),
                        password: str = Form(...),
                        password2: str = Form(...),
                        db: Session = Depends(get_db)
                        ):

    # Valido que el usuario no esté ya registrado, y que el password haya sido bien ingresado
    validation1 = db.query(models.Users).filter(models.Users.username == username).first()
    validation2 = db.query(models.Users).filter(models.Users.email == email).first()
    validation3 = True if password == password2 else None

    if validation1 is not None or validation2 is not None or validation3 is None:
        msg = "Datos de registro inválidos"
        return templates. TemplateResponse("register.html", {"request":request, "msg": msg})

    user_model = models.Users()
    user_model.username = username
    user_model.email = email
    user_model.first_name = firstname
    user_model.last_name = lastname
    user_model.hashed_password = get_password_hash(password) # Encripto el password
    user_model.is_active = True

    db.add(user_model)
    db.commit()  

    msg = "Usuario Creado"
    return templates.TemplateResponse("login.html", {"request":request, "msg": msg})
