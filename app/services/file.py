import os
import uuid
from pathlib import Path
from app.models.file import File
from app.models.tag import Tag
from app.database import SessionDep
from sqlmodel import select
from fastapi import HTTPException, UploadFile

# Path is overridable so deployments can point it at a persistent volume.
UPLOAD_DIR = Path(os.environ.get("UPLOAD_DIR", "uploads"))

def upload_file(upload: UploadFile, user_id: int, session: SessionDep, tag_ids: list[int] | None = None) -> File:
    # Resolve the tags first, so an invalid tag aborts before we write to disk.
    # With no tag_ids this loop runs zero times and the file is created untagged.
    tags = []
    for tag_id in tag_ids or []:
        tag = session.exec(select(Tag).where(Tag.id == tag_id)).first()
        # 404 if the tag doesn't exist or isn't the uploader's own.
        if not tag or tag.user_id != user_id:
            raise HTTPException(status_code=404, detail="tag not found")
        tags.append(tag)

    # Double check folder exists.
    UPLOAD_DIR.mkdir(exist_ok=True)

    # Save files cleansed and for avoiding duplicates with the UUID
    key = f"{uuid.uuid4()}_{upload.filename}"
    dest = UPLOAD_DIR / key

    # Read the uploaded bytes and write them to disk.
    contents = upload.file.read()
    dest.write_bytes(contents)

    # File Metadata for db
    db_file = File(
        filename=upload.filename,          # Display filename
        path=str(dest),                    # Storage Location, where does the file live on disk?
        content_type=upload.content_type,  # Type of file
        size=len(contents),                # size of file in bytes
        user_id=user_id,                   # owner of the file
        tags=tags,                         # 0 or more tags attached at upload
    )

    session.add(db_file)
    session.commit()
    session.refresh(db_file)
    return db_file

def get_files(session: SessionDep, user_id: int, offset: int = 0, limit: int = 100):
    files = session.exec(
        select(File).where(File.user_id == user_id).offset(offset).limit(limit)
    ).all()
    return files

def get_file(file_id: int, user_id: int, session: SessionDep) -> File:
    file = session.exec(select(File).where(File.id == file_id)).first()
    # 404 (not 403) for security reasons, so the files existence isn't leaked.
    if not file or file.user_id != user_id:
        raise HTTPException(status_code=404, detail="file not found")
    return file

def delete_file(file_id: int, user_id: int, session: SessionDep):
    file = get_file(file_id, user_id, session)
    # Removes file from disl, then from db
    Path(file.path).unlink(missing_ok=True)
    session.delete(file)
    session.commit()
    return {"ok": True}