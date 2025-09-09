import logging
from datetime import datetime

from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker

logger = logging.getLogger(__name__)


class Session(BaseModel):
    id: int
    user_id: int
    token: str
    created_timestamp: datetime


class SessionsRepository:
    def __init__(self, db: async_sessionmaker):
        self.db = db

    async def get_by_token(self, token: str) -> Session | None:
        sql = """
            SELECT *
            FROM "user_sessions"
            WHERE "token" = :token
        """
        async with self.db() as session:
            async with session.begin():
                result = await session.execute(text(sql), {"token": token})
        if result:
            result = result.mappings().all()
            if len(result) > 0:
                result = Session(**result[0])
                return result
        return None

    async def create(self, user_id: int, token: str) -> Session | None:

        sql = """
            INSERT INTO "user_sessions" (user_id, token)
            VALUES (:user_id, :token)
            ON CONFLICT (user_id) DO UPDATE SET token = :token
            RETURNING *
        """

        async with self.db() as session:
            async with session.begin():
                result = await session.execute(
                    text(sql), {"user_id": user_id, "token": token}
                )
        if result:
            result = result.mappings().all()
            if len(result) > 0:
                result = Session(**result[0])
                return result
        return None

    async def get_by_user_id(self, user_id: int) -> Session | None:
        sql = """
            SELECT *
            FROM "user_sessions"
            WHERE "user_id" = :user_id
        """
        async with self.db() as session:
            async with session.begin():
                result = await session.execute(text(sql), {"user_id": user_id})
        if result:
            result = result.mappings().all()
            if len(result) > 0:
                result = Session(**result[0])
                return result
        return None

    async def delete(self, id: int):
        sql = """
            DELETE FROM "user_sessions"
            WHERE id = :id
        """
        async with self.db() as session:
            async with session.begin():
                await session.execute(text(sql), {"id": id})
        return
