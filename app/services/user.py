from app.schemas.user import UserCreate
from app.models.user import User
from app.database import SessionDep
from sqlmodel import select
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

def create_user(user: UserCreate, session: SessionDep) -> User:
    db_user = User.model_validate(user)
    session.add(db_user)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="Email already exists")
    session.refresh(db_user)
    return db_user

def get_users(session: SessionDep, offset: int = 0, limit: int = 100) -> list[User]:
    users = session.exec(select(User).offset(offset).limit(limit)).all()
    return users

def get_user(user_id: int, session: SessionDep,) -> User:
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def delete_user(user_id: int, session: SessionDep) -> dict:
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    session.commit()
    return {"ok": True}