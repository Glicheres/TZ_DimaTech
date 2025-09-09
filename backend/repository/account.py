import logging
from datetime import datetime

from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker

logger = logging.getLogger(__name__)


class Account(BaseModel):
    id: int
    user_id: int
    balance: int
    created_timestamp: datetime


class AccountRepository:
    def __init__(self, db: async_sessionmaker):
        self.db = db

    async def get_by_user_id(self, user_id: int) -> list[Account]:
        sql = """
            SELECT *
            FROM "accounts"
            WHERE "user_id" = :user_id
        """
        async with self.db() as session:
            async with session.begin():
                data = await session.execute(text(sql), {"user_id": user_id})
        data = data.mappings().all()
        return [Account(**account) for account in data]
