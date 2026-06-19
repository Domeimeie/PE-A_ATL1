from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from app.models.user import User
from app.models.tag import Tag, FileTagLink

class File(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    filename: str
    path: str
    content_type: str | None = None
    size: int | None = None
    user_id: int = Field(foreign_key="user.id")
    user: User | None = Relationship(back_populates="files")
    tags: list["Tag"] = Relationship(back_populates="files", link_model=FileTagLink)
    uploaded_at: datetime = Field(default_factory=datetime.now, nullable=False)
