import asyncio
import logging

import uvicorn
from fastapi import FastAPI

import backend.log as log
import backend.migrations_runner as migrations_runner
from backend import conf
from backend.state import app_state

log.setup_logging()
logger = logging.getLogger(__name__)


app = FastAPI()


@app.on_event("startup")
async def setup():
    await asyncio.sleep(5)
    migrations_runner.apply()
    await app_state.startup()


@app.on_event("shutdown")
async def shutdown():
    await app_state.shutdown()


if __name__ == "__main__":
    """
    Точка в хода в основной веб сервер.
    Обрабатывает запросы от ТГ.
    """
    uvicorn.run(
        app="backend.app:app",
        host="0.0.0.0",
        port=8080,
        reload=conf.AUTO_RELOAD,
        access_log=False,
    )
