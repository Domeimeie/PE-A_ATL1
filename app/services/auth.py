from app.models.user import User
from app.database import SessionDep
from sqlmodel import select
from fastapi import HTTPException
import jwt

from app.schemas.jwt import JwtPublic

jwt_secret = "secretsecretsecretsecretsecretsecret"
jwt_algorithm = "HS256"

def authenticate_user(email: str, password: str, session: SessionDep) -> User:
    user = session.exec(select(User).where(User.email == email)).first()
    if not user or password != user.password:
        raise HTTPException(status_code=401, detail="Invalid Login Details")
    return user

def create_jwt(user: User) -> JwtPublic:
     payload_jwt= {
         "user.id": user.id
     }
     encoded_jwt = jwt.encode(payload_jwt, jwt_secret, algorithm=jwt_algorithm)
     return JwtPublic(access_token=encoded_jwt)