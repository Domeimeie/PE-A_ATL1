from pydantic import BaseModel

class JwtPublic(BaseModel):
    access_token: str