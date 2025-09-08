from pydantic import BaseModel


class UserAuthBody(BaseModel):
    email: str
    password: str


class GetUserResponse(BaseModel):
    id: int
    email: str
    username: str
