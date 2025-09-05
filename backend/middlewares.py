import logging
from contextvars import ContextVar
from uuid import uuid4

from fastapi import Request, Response
from starlette.routing import Match

logger = logging.getLogger(__name__)
request_id_contextvar = ContextVar("request_id_contextvar")


def _get_url_name(request: Request) -> str:
    for route in request.app.routes:
        match, _ = route.matches(request.scope)
        if match == Match.FULL:
            return route.path

    return "not_matched"


async def request_id_middleware(request: Request, call_next):
    """
    Добавляет request_id в контекст.
    """
    request_id = request.headers.get("X-Request-Id")
    if not request_id:
        request_id = str(uuid4())

    token = request_id_contextvar.set(request_id)
    try:
        return await call_next(request)
    finally:
        request_id_contextvar.reset(token)


async def access_log_middleware(request: Request, call_next):
    status = None
    try:
        response: Response = await call_next(request)
        status = response.status_code
        return response
    except Exception:
        status = 500
        raise
    finally:
        logger.info("%s %s %s", status, request.method, request.url)
