from pydantic import BaseModel


class AdminCreateUserBody(BaseModel):
    username: str
    email: str
    password: str
