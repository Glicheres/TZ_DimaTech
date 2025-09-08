import json

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

import backend.conf as conf
from backend.repository.sessions import SessionsRepository
from backend.repository.users import UserRepository


class AppState:
    def __init__(self) -> None:
        self._async_engine = None
        self._async_sessionmaker = None
        self._user_repository = None
        self._sessions_repository = None

    async def startup(self) -> None:
        # Создаем асинхронный engine с использованием asyncpg
        self._async_engine = create_async_engine(
            conf.DATABASE_DSN.replace("postgresql", "postgresql+asyncpg", 1),
            echo=False,
            json_serializer=json.dumps,
            json_deserializer=json.loads,
            poolclass=NullPool,
        )
        # Создаем фабрику сессий
        self._async_sessionmaker = async_sessionmaker(
            bind=self._async_engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

        self._user_repository = UserRepository(db=self._async_sessionmaker)
        self._sessions_repository = SessionsRepository(
            db=self._async_sessionmaker
        )

    async def shutdown(self) -> None:
        if self._async_engine:
            await self._async_engine.dispose()

    @property
    def db(self) -> async_sessionmaker:
        assert self._async_sessionmaker
        return self._async_sessionmaker

    @property
    def user_repo(self) -> UserRepository:
        assert self._user_repository
        return self._user_repository

    @property
    def session_repo(self) -> SessionsRepository:
        assert self._sessions_repository
        return self._sessions_repository


app_state = AppState()
