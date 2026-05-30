from typing import Annotated
from fastapi import APIRouter, Query
from app.schemas.file import FileUpload, FilePublic
from app.services.file import (
    upload_file as upload_file_service,
    get_files as get_files_service,
    delete_file as delete_file_service,
    get_file as get_file_service
)
from app.database import SessionDep


router = APIRouter(prefix="/files", tags=["files"])

@router.post("/", response_model=FilePublic)
def create_file(file: FileUpload, session: SessionDep):
    return upload_file_service(file, session)


@router.get("/", response_model=list[FilePublic])
def get_files(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    return get_files_service(session, offset, limit)
    
@router.get("/{file_id}", response_model=FilePublic)
def get_file(file_id: int, session: 
    SessionDep):
    return get_file_service(file_id, session)

@router.delete("/{file_id}")
def delete_file(file_id: int, session: SessionDep):
    return delete_file_service(file_id, session)