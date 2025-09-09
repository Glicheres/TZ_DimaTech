from pydantic import BaseModel


class AdminCreateUserBody(BaseModel):
    username: str
    email: str
    password: str


class UpdateUserBody(BaseModel):
    id: int
    username: str
    email: str
    password: str
