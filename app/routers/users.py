from fastapi import APIRouter, Query
from app.services.user import (
    create_user as create_user_service,
    get_users as get_users_service,
    get_user as get_user_service,
    delete_user as delete_user_service,
)
from app.schemas.user import UserPublic, UserCreate
from app.database import SessionDep
from typing import Annotated

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/")
def create_user(user: UserCreate, session: SessionDep) -> UserPublic:
    return create_user_service(user=user, session=session)

@router.get("/")
def get_users(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[UserPublic]:
    return get_users_service(session=session, offset=offset, limit=limit)

@router.get("/{user_id}")
def get_user(user_id: int, session: SessionDep) -> UserPublic:
    return get_user_service(user_id=user_id, session=session)

@router.delete("/{user_id}")
def delete_user(user_id: int, session: SessionDep) -> dict:
    return delete_user_service(user_id=user_id, session=session)