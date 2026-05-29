from fastapi import APIRouter
from app.services.auth import authenticate_user, create_jwt
from app.schemas.user import UserLogin
from app.database import SessionDep

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login")
def login(credentials: UserLogin, session: SessionDep):
    user = authenticate_user(email=credentials.email, password=credentials.password, session=session)
    return create_jwt(user)
