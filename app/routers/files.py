from typing import Annotated
from fastapi import APIRouter, Query, UploadFile, Depends
from fastapi.responses import FileResponse
from app.schemas.file import FilePublic
from app.security import token_auth
from app.services.file import (
    upload_file as upload_file_service,
    get_files as get_files_service,
    delete_file as delete_file_service,
    get_file as get_file_service
)
from app.database import SessionDep


router = APIRouter(prefix="/files", tags=["files"])

@router.post("/", response_model=FilePublic)
def upload_file(
    session: SessionDep,
    upload: UploadFile,
    token: Annotated[dict, Depends(token_auth)],
):
    # Take user ID from token
    user_id = token["user.id"]
    return upload_file_service(upload, user_id, session)


@router.get("/", response_model=list[FilePublic])
def get_files(
    session: SessionDep,
    token: Annotated[dict, Depends(token_auth)],
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    return get_files_service(session, token["user.id"], offset, limit)

@router.get("/{file_id}")
def download_file(
    file_id: int,
    session: SessionDep,
    token: Annotated[dict, Depends(token_auth)],
):
    file = get_file_service(file_id, token["user.id"], session)
    return FileResponse(file.path, filename=file.filename, media_type=file.content_type)

@router.delete("/{file_id}")
def delete_file(
    file_id: int,
    session: SessionDep,
    token: Annotated[dict, Depends(token_auth)],
):
    return delete_file_service(file_id, token["user.id"], session)