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

    async def get_id(self, id: int) -> Account | None:
        sql = """
            SELECT *
            FROM "accounts"
            WHERE "id" = :id
        """
        async with self.db() as session:
            async with session.begin():
                result = await session.execute(text(sql), {"id": id})
        if result:
            result = result.mappings().all()
            if len(result) > 0:
                result = Account(**result[0])
                return result
        return None

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

    async def create(
        self, id: int, user_id: int, balance: int
    ) -> Account | None:
        sql = """
            INSERT INTO "accounts" (id ,user_id, balance)
            VALUES (:id, :user_id, :balance)
            RETURNING *
        """
        async with self.db() as session:
            async with session.begin():
                result = await session.execute(
                    text(sql),
                    {"id": id, "user_id": user_id, "balance": balance},
                )
        if result:
            result = result.mappings().all()
            if len(result) > 0:
                result = Account(**result[0])
                return result
        return None

    async def increase(self, account_id: int, balance_increase: int):
        sql = """
            UPDATE "accounts"
            SET balance = balance + :balance_increase
            WHERE id = :account_id
        """
        async with self.db() as session:
            async with session.begin():
                await session.execute(
                    text(sql),
                    {
                        "account_id": account_id,
                        "balance_increase": balance_increase,
                    },
                )
