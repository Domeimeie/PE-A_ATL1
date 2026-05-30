from app.models.file import File
from app.schemas.file import FileUpload
from app.database import SessionDep
from sqlmodel import select
from fastapi import HTTPException

def upload_file(file: FileUpload, session: SessionDep):
    db_file = File.model_validate(file)
    session.add(db_file)
    session.commit()
    session.refresh(db_file)
    return db_file

def get_files(session: SessionDep, offset: int = 0, limit: int = 100):
    files = session.exec(select(File).offset(offset).limit(limit)).all()
    return files

def get_file(file_id: int, session: SessionDep) -> File:
    file = session.exec(select(File).where(File.id == file_id)).first()
    if not file:
        raise HTTPException(status_code=404, detail="file not found")
    return file

def delete_file(file_id: int, session: SessionDep):
    file = session.get(File, file_id)
    if not file:
        raise HTTPException(status_code=404, detail="file not found")
    session.delete(file)
    session.commit()
    return {"ok": True}