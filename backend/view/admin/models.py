from pydantic import BaseModel


class AdminCreateUserBody(BaseModel):
    username: str
    email: str
    password: str


class UpdateUserBody(BaseModel):
    username: str
    email: str
    password: str
