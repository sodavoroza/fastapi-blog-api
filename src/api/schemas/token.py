from pydantic import BaseModel


class TokenResponse(BaseModel):
    message: str
    access_token: str
    token_type: str
