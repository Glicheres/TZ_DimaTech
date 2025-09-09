import logging
from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, Response, status

from backend.helper import check_session, cookie_create, hash_password
from backend.repository.users import User
from backend.state import app_state
from backend.view.user.models import GetUserResponse, UserAuthBody

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/user/auth")
async def auth_users(
    response: Response, body: Annotated[UserAuthBody, Body()]
):
    """
    Авторизация пользователя
    """
    exist_user = await app_state.user_repo.get_email(email=body.email)

    if not exist_user:
        logger.info("User does not exist")
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="User does not exist"
        )

    db_user = await app_state.user_repo.get_email(email=body.email)

    if db_user.password != hash_password(password=body.password):
        logger.info("Access denied - wrong password")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied - wrong password",
        )

    token = cookie_create(email=body.email)

    await app_state.session_repo.create(user_id=db_user.id, token=token)
    response.set_cookie(key="cookie", value=token)
    return token


@router.get("/user")
async def get_users(user: User = Depends(check_session)):
    """
    Получение данных о пользователе
    """

    return GetUserResponse(
        id=user.id, username=user.username, email=user.email
    )
