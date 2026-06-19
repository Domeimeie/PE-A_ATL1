from typing import Annotated
from fastapi import APIRouter, Query, Depends
from app.schemas.tag import TagCreate, TagPublic
from app.schemas.file import FilePublic
from app.security import token_auth
from app.services.tag import (
    create_tag as create_tag_service,
    get_tags as get_tags_service,
    get_tag as get_tag_service,
    get_files_by_tag as get_files_by_tag_service,
    delete_tag as delete_tag_service,
)
from app.database import SessionDep


router = APIRouter(prefix="/tags", tags=["tags"])

@router.post("/", response_model=TagPublic)
def create_tag(
    tag: TagCreate,
    session: SessionDep,
    token: Annotated[dict, Depends(token_auth)],
):
    return create_tag_service(tag, token["user.id"], session)


@router.get("/", response_model=list[TagPublic])
def get_tags(
    session: SessionDep,
    token: Annotated[dict, Depends(token_auth)],
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    return get_tags_service(session, token["user.id"], offset, limit)

@router.get("/{tag_id}", response_model=TagPublic)
def get_tag(
    tag_id: int,
    session: SessionDep,
    token: Annotated[dict, Depends(token_auth)],
):
    return get_tag_service(tag_id, token["user.id"], session)

@router.get("/{tag_id}/files", response_model=list[FilePublic])
def get_files_by_tag(
    tag_id: int,
    session: SessionDep,
    token: Annotated[dict, Depends(token_auth)],
):
    return get_files_by_tag_service(tag_id, token["user.id"], session)

@router.delete("/{tag_id}")
def delete_tag(
    tag_id: int,
    session: SessionDep,
    token: Annotated[dict, Depends(token_auth)],
):
    return delete_tag_service(tag_id, token["user.id"], session)
