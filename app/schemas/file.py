from datetime import datetime
from pydantic import BaseModel
from app.schemas.user import UserPublic
from app.schemas.tag import TagPublic

class FilePublic(BaseModel):
    id: int
    user: UserPublic
    filename: str
    content_type: str | None = None
    size: int | None = None
    uploaded_at: datetime
    tags: list[TagPublic] = []