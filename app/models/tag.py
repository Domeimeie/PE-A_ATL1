from sqlmodel import SQLModel, Field, Relationship
from app.models.user import User

class FileTagLink(SQLModel, table=True):
    file_id: int | None = Field(default=None, foreign_key="file.id", primary_key=True)
    tag_id: int | None = Field(default=None, foreign_key="tag.id", primary_key=True)

class Tag(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    user_id: int = Field(foreign_key="user.id")
    user: User | None = Relationship(back_populates="tags")
    files: list["File"] = Relationship(back_populates="tags", link_model=FileTagLink)
