import logging

from fastapi import APIRouter, Depends, HTTPException, status

from backend.helper import check_session, hash_password
from backend.repository.users import User
from backend.state import app_state
from backend.view.admin.models import AdminCreateUserBody, UpdateUserBody
from backend.view.user.models import GetUserResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.put("/user")
async def create_users(
    body: AdminCreateUserBody, admin: User = Depends(check_session)
):
    """
    Создание пользователя
    """
    if not admin.is_admin:
        logger.info("Access denied")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    exist_user = await app_state.user_repo.get_email(email=body.email)

    if exist_user:
        logger.info("User already exist")
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="User already exist"
        )

    # шифруем пароль
    salt_password = hash_password(password=body.password)
    logger.info(salt_password)

    user = await app_state.user_repo.create(
        username=body.username, email=body.email, salt_password=salt_password
    )
    return user


@router.get("/users")
async def get_all_users(admin: User = Depends(check_session)):
    if not admin.is_admin:
        logger.info("Access denied")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
    users = await app_state.user_repo.get_all()
    return users


@router.get("/user/{id}")
async def get_users(id: int, user: User = Depends(check_session)):
    """
    Получение данных о пользователе (админом)
    """
    if not user.is_admin:
        logger.info("Access denied")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
    else:
        required_user = await app_state.user_repo.get_id(id=id)
        if not required_user:
            logger.info("User does not exist")
            return HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User does not exist",
            )
        return GetUserResponse(
            id=required_user.id,
            username=required_user.username,
            email=required_user.email,
        )


@router.post("/user/{id}")
async def update_user(
    id: int, body: UpdateUserBody, admin: User = Depends(check_session)
):
    """
    Изменение пользователя
    """
    if not admin.is_admin:
        logger.info("Access denied")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
    sault_pass = hash_password(password=body.password)

    user = await app_state.user_repo.update(
        id=id,
        username=body.username,
        email=body.email,
        password=sault_pass,
    )
    if not user:
        logger.info("User does not exist")
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User does not exist",
        )
    return user


@router.delete("/user/{id}")
async def delete_user(id: int, admin: User = Depends(check_session)):
    """
    Удаление пользователя
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
    session = await app_state.session_repo.get_by_user_id(user_id=user.id)
    if session:
        await app_state.session_repo.delete(id=session.id)

    await app_state.user_repo.delete(id=id)

    return HTTPException(status_code=status.HTTP_200_OK)
