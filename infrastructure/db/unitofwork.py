import asyncio
from contextlib import AbstractAsyncContextManager

from sqlalchemy.ext.asyncio import async_scoped_session, async_sessionmaker
from sqlalchemy.ext.asyncio.session import AsyncSession

from infrastructure.db.engine import ABCDatabaseEngine
from utils.logging import Logging


class ABCUnitOfWork(AbstractAsyncContextManager[AsyncSession]):
    ...


class SQLAlchemyUnitOfWork(ABCUnitOfWork):
    def __init__(self, logging: Logging, db_engine: ABCDatabaseEngine):
        self._logger = logging.get_logger(__name__)
        self._db_engine = db_engine
        self._session_maker = async_scoped_session(
            async_sessionmaker(bind=db_engine.get_engine()),  # type: ignore
            scopefunc=asyncio.current_task,
        )

    async def __aenter__(self):
        self.session = self._session_maker()
        return self.session

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.session.expunge_all()
        if exc_type is not None:
            await self.session.rollback()
        else:
            await self.session.commit()
        await asyncio.shield(self.session.close())
