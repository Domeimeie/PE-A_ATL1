from typing import Annotated
from fastapi import APIRouter, Query, UploadFile, Depends, Form, HTTPException
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
    tag_ids: Annotated[list[str], Form()] = [],
):
    # Take user ID from token
    user_id = token["user.id"]
    # Swagger UI sends a multipart array as one comma-joined field ("4,5"),
    # while curl/clients may send repeated fields. Accept both: split each
    # value on commas and flatten to a list of ints.
    parsed_tag_ids = []
    for value in tag_ids:
        for part in value.split(","):
            part = part.strip()
            if not part:
                continue
            try:
                parsed_tag_ids.append(int(part))
            except ValueError:
                raise HTTPException(status_code=422, detail=f"invalid tag id: {part}")
    return upload_file_service(upload, user_id, session, parsed_tag_ids)


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