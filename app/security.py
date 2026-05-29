from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
import jwt

jwt_secret = "secretsecretsecretsecretsecretsecret"
jwt_algorithm = "HS256"

bearer_scheme = HTTPBearer()

def token_auth(token = Depends(bearer_scheme)):
    try:
        return jwt.decode(token.credentials, jwt_secret, algorithms=[jwt_algorithm])
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
