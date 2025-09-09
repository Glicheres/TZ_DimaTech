import asyncio
import logging

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import backend.log as log
import backend.migrations_runner as migrations_runner
from backend import conf
from backend.state import app_state
from backend.view.accounts.view import router as account_router
from backend.view.admin.view import router as admin_router
from backend.view.payment.view import router as payment_router
from backend.view.user.view import router as user_router

log.setup_logging()
logger = logging.getLogger(__name__)


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router)
app.include_router(admin_router)
app.include_router(account_router)
app.include_router(payment_router)


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
    """
    uvicorn.run(
        app="backend.app:app",
        host="0.0.0.0",
        port=8080,
        reload=conf.AUTO_RELOAD,
        access_log=False,
    )
