from pydantic import BaseModel

class UserCreate(BaseModel):
    email: str
    password: str

class UserPublic(BaseModel):
    id: int
    email: str