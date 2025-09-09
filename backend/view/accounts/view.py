import logging

from fastapi import APIRouter, Depends, HTTPException, status

from backend.helper import check_session
from backend.repository.users import User
from backend.state import app_state

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/accounts")
async def get_accounts(user: User = Depends(check_session)):
    """
    Получение счетов пользователя
    """
    accounts = await app_state.account_repo.get_by_user_id(user_id=user.id)
    return accounts


@router.get("/user/{id}/accounts")
async def get_user_accounts(id: int, admin: User = Depends(check_session)):
    """
    Получение счетов пользователя (админом)
    """
    if not admin.is_admin:
        logger.info("Access denied")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
    user = await app_state.user_repo.get_id(id=id)
    if not user:
        logger.info("User does not exist")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User does not exist",
        )

    accounts = await app_state.account_repo.get_by_user_id(user_id=user.id)
    return accounts
