from pydantic import BaseModel


class PaymentBody(BaseModel):
    user_id: int
    account_id: int
    amount: int
    transaction_id: str
    signature: str
