from pydantic import BaseModel

class UserCreate(BaseModel):
    email: str
    password: str

class UserLogin(UserCreate):
    pass

class UserPublic(BaseModel):
    id: int
    email: str