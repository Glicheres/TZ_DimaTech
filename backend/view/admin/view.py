import logging

from fastapi import APIRouter, Depends, HTTPException, status

from backend.helper import check_session, hash_password
from backend.repository.users import User
from backend.state import app_state
from backend.view.admin.models import AdminCreateUserBody

logger = logging.getLogger(__name__)
router = APIRouter()


@router.put("/user")
async def create_users(
    body: AdminCreateUserBody, admin: User = Depends(check_session)
):
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
