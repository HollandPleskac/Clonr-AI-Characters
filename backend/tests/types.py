from pydantic import BaseModel


# doing this to prevent passing a mutable dict everywhere
class LoginData(BaseModel):
    email: str
    password: str
