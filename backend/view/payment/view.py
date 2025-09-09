import logging

from fastapi import APIRouter, Depends, HTTPException, status

from backend.helper import check_session, signature_payment_check
from backend.repository.users import User
from backend.state import app_state
from backend.view.payment.models import PaymentBody

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/webhook/payment")
async def create_payment(body: PaymentBody):
    """
    Обработка вебхука - создание платежа
    """
    is_correct_signature = signature_payment_check(
        user_id=body.user_id,
        account_id=body.account_id,
        amount=body.amount,
        transaction_id=body.transaction_id,
        signature=body.signature,
    )
    if not is_correct_signature:
        logger.info("Wrong signature")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Wrong signature"
        )
    account = await app_state.account_repo.get_id(id=body.account_id)
    if not account:
        user = await app_state.user_repo.get_id(id=body.user_id)
        if not user:
            logger.info("User does not exist")
            return HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User does not exist",
            )
        account = await app_state.account_repo.create(
            id=body.account_id, user_id=body.user_id, balance=body.amount
        )
    if account.user_id != body.user_id:
        logger.info("Wrong user id or account id")
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Wrong user id or account id",
        )
    # Уникальность транзакции проверяется в sql запросе
    payment = await app_state.payment_repo.create(
        user_id=body.user_id,
        account_id=body.account_id,
        amount=body.amount,
        transaction_id=body.transaction_id,
    )

    if payment:
        await app_state.account_repo.increase(
            account_id=body.account_id, balance_increase=body.amount
        )

    return HTTPException(status_code=status.HTTP_200_OK)


@router.get("/payment")
async def get_accounts(user: User = Depends(check_session)):
    """
    Получение платежей пользователя
    """
    payments = await app_state.payment_repo.get_by_user_id(user_id=user.id)
    return payments
