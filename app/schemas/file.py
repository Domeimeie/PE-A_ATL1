from datetime import datetime
from pydantic import BaseModel, Field
from app.schemas.user import UserPublic

class FileUpload(BaseModel):
    user_id: int
    filename: str

class FilePublic(BaseModel):
    id: int
    user: UserPublic
    filename: str
    uploaded_at: datetime