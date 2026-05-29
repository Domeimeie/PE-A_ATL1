from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import create_db_and_tables
from app.routers.users import router as users_router
from app.routers.auth import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
   create_db_and_tables()
   yield

app = FastAPI(lifespan=lifespan)

app.include_router(users_router)
app.include_router(auth_router)

@app.get("/")
def get_root():
   return{"message": "Welcome to the state of the art File upload system \"DODOload\""}