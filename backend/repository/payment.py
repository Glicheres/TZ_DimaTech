import logging
from datetime import datetime

from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker

logger = logging.getLogger(__name__)


class Payment(BaseModel):
    id: int
    user_id: int
    account_id: int
    amount: int
    transaction_id: str
    created_timestamp: datetime


class PaymentRepository:
    def __init__(self, db: async_sessionmaker):
        self.db = db

    async def create(
        self, user_id: int, account_id: int, amount: int, transaction_id: str
    ) -> Payment | None:
        sql = """
            INSERT INTO "payment"
                (user_id, account_id, amount, transaction_id)
            VALUES (:user_id, :account_id, :amount, :transaction_id)
            ON CONFLICT (transaction_id) DO NOTHING
            RETURNING *
        """
        async with self.db() as session:
            async with session.begin():
                result = await session.execute(
                    text(sql),
                    {
                        "user_id": user_id,
                        "account_id": account_id,
                        "amount": amount,
                        "transaction_id": transaction_id,
                    },
                )
        if result:
            result = result.mappings().all()
            if len(result) > 0:
                result = Payment(**result[0])
                return result
        return None

    async def get_by_user_id(self, user_id: int) -> list[Payment]:
        sql = """
               SELECT *
               FROM "payment"
               WHERE "user_id" = :user_id
           """
        async with self.db() as session:
            async with session.begin():
                data = await session.execute(text(sql), {"user_id": user_id})
        data = data.mappings().all()
        return [Payment(**account) for account in data]
