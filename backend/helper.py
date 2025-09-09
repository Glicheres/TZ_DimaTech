import base64
import hashlib
import hmac
import logging

from fastapi import Cookie, HTTPException, status

from backend.conf import COOKIE_SECRET_KEY, PASSWORD_SALT, WEBHOOK_SECRET_KEY
from backend.repository.users import User
from backend.state import app_state

logger = logging.getLogger(__name__)


def _sign_data(data: str) -> str:
    # подписываем данные
    return (
        hmac.new(
            COOKIE_SECRET_KEY.encode(),
            msg=data.encode(),
            digestmod=hashlib.sha256,
        )
        .hexdigest()
        .upper()
    )


def cookie_create(email: str) -> str:
    # Кодирование cookie
    return base64.b64encode(email.encode()).decode() + "." + _sign_data(email)


def cookie_decode(username_signed: str) -> str | None:
    # Декодирование cookie
    if len(username_signed) > 0 and "." in username_signed:
        username_b64, sign = username_signed.split(".")
        username = base64.b64decode(username_b64.encode()).decode()
        valid_sign = _sign_data(username)
        if hmac.compare_digest(valid_sign, sign):
            return username
        else:
            return None


def hash_password(password: str) -> str:
    # Хеширование пароля
    return (
        hashlib.sha256((password + PASSWORD_SALT).encode()).hexdigest().lower()
    )


async def check_session(cookie: str | None = Cookie(default=None)) -> User:
    # Зависимость для проверки cockie

    if not cookie:
        logger.info("No session cookie.")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    user_mail = cookie_decode(cookie)
    if not user_mail:
        logger.info("Wrong session cookie.")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    user = await app_state.user_repo.get_email(email=user_mail)
    if not user:
        logger.info("User not found.")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    session = await app_state.session_repo.get_by_token(token=cookie)
    if not session:
        logger.info("Session not found.")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    if session.user_id == user.id:
        return user
    else:
        logger.info("Invalid user")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


def signature_payment_check(
    user_id: int,
    account_id: int,
    amount: int,
    transaction_id: str,
    signature: str,
):
    signature_str = (
        f"{account_id}{amount}"
        f"{transaction_id}{user_id}{WEBHOOK_SECRET_KEY}"
    )
    generaded_signature = hashlib.sha256(signature_str.encode()).hexdigest()
    return generaded_signature == signature
