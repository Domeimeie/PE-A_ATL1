from pydantic import BaseModel
from app.schemas.user import UserPublic

class TagCreate(BaseModel):
    name: str

class TagPublic(BaseModel):
    id: int
    user: UserPublic
    name: str
