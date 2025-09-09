import logging
from datetime import datetime

from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker

logger = logging.getLogger(__name__)


class User(BaseModel):
    id: int
    username: str
    email: str
    is_admin: bool
    password: str
    created_timestamp: datetime


class UserRepository:
    # можно сделать декоратор - обёртку для "фабрики" функций
    def __init__(self, db: async_sessionmaker):
        self.db = db

    async def get_id(self, id: int) -> User | None:
        sql = """
            SELECT *
            FROM "users"
            WHERE "id" = :id
        """
        async with self.db() as session:
            async with session.begin():
                result = await session.execute(text(sql), {"id": id})
        if result:
            result = result.mappings().all()
            if len(result) > 0:
                result = User(**result[0])
                return result
        return None

    async def get_email(self, email: str) -> User | None:
        sql = """
            SELECT *
            FROM "users"
            WHERE "email" = :email
        """
        async with self.db() as session:
            async with session.begin():
                result = await session.execute(text(sql), {"email": email})
        if result:
            result = result.mappings().all()
            if len(result) > 0:
                result = User(**result[0])
                return result
        return None

    async def create(
        self, username: str, email: str, salt_password: str
    ) -> User | None:
        sql = """
            INSERT INTO "users" (username, email, password)
            VALUES (:username, :email, :password)
            RETURNING *
        """
        async with self.db() as session:
            async with session.begin():
                result = await session.execute(
                    text(sql),
                    {
                        "username": username,
                        "email": email,
                        "password": salt_password,
                    },
                )
        if result:
            result = result.mappings().all()
            if len(result) > 0:
                result = User(**result[0])
                return result
        return None

    async def get_all(self) -> list[User]:
        sql = """
            SELECT *
            FROM "users"
        """
        async with self.db() as session:
            async with session.begin():
                data = await session.execute(text(sql), {"id": id})
            data = data.mappings().all()
            return [User(**user) for user in data]

    async def update(
        self, id: int, username: str, email: str, password: str
    ) -> User | None:
        sql = """
            UPDATE users
            SET username = :username, email = :email, password = :password
            WHERE id = :id
            RETURNING *
        """
        async with self.db() as session:
            async with session.begin():
                result = await session.execute(
                    text(sql),
                    {
                        "id": id,
                        "username": username,
                        "email": email,
                        "password": password,
                    },
                )
            if result:
                result = result.mappings().all()
                if len(result) > 0:
                    result = User(**result[0])
                    return result
            return None

    async def delete(self, id: int):
        sql = """
            DELETE FROM users
            WHERE id = :id
        """
        async with self.db() as session:
            async with session.begin():
                await session.execute(text(sql), {"id": id})
        return
