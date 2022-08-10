from fastapi import FastAPI, Depends
import models              
from database import engine
from routers import auth, todos, users
from starlette.staticfiles import StaticFiles
from starlette import status
from starlette.responses import RedirectResponse

app = FastAPI()

# Creo la base de datos con los modelos definidos
models.Base.metadata.create_all(bind=engine)

# Montamos archivos estaticos como css, js, etc.
app.mount("/static", StaticFiles(directory="static"), name="static")

# Hago esto para que todo lo que caiga en la url / vaya a todos
@app.get("/")
async def root():
    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)

# Agrego el router a las API's
app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(users.router)



