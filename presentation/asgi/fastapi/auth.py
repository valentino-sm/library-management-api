import logging
import uuid
from typing import Any, AsyncGenerator, Callable, Protocol

from fastapi.routing import APIRouter
from fastapi_users import FastAPIUsers
from fastapi_users.authentication.backend import AuthenticationBackend
from fastapi_users.authentication.strategy.jwt import JWTStrategy
from fastapi_users.authentication.transport.bearer import BearerTransport
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase

from infrastructure.db.models.models import User
from infrastructure.db.unitofwork import ABCUnitOfWork
from presentation.asgi.fastapi.user_manager import UserManager
from utils.logging import Logging

# Temporarily fix bcrypt>=4.1 warning
logging.getLogger("passlib.handlers.bcrypt").setLevel(logging.ERROR)


class ABCAuthService(Protocol):
    def add_auth_routes_to(
        self, router: APIRouter, user_read_schema: Any, user_create_schema: Any
    ) -> None:
        raise NotImplementedError

    def add_user_routes_to(
        self, router: APIRouter, user_read_schema: Any, user_update_schema: Any
    ) -> None:
        raise NotImplementedError

    def current_user(
        self, active: bool = False, verified: bool = False, superuser: bool = False
    ) -> Callable[[], User]:
        raise NotImplementedError


class FastAPIUsersService(ABCAuthService):
    def __init__(
        self, logging: Logging, uow: ABCUnitOfWork, secret: str, token_url: str
    ) -> None:
        self._logger = logging.get_logger(__name__)
        self._uow = uow
        self._secret = secret

        self._auth_backend = AuthenticationBackend(
            name="jwt",
            transport=BearerTransport(tokenUrl=token_url),
            get_strategy=self._get_jwt_strategy,
        )
        self._fastapi_users = FastAPIUsers[User, uuid.UUID](
            self._get_user_manager, [self._auth_backend]
        )

    def _get_jwt_strategy(self) -> JWTStrategy[Any, Any]:
        return JWTStrategy(secret=self._secret + "_jwt", lifetime_seconds=3600)

    async def _get_user_manager(self) -> AsyncGenerator[UserManager, None]:
        async with self._uow as session:
            yield UserManager(
                user_db=SQLAlchemyUserDatabase(
                    session=session,
                    user_table=User,
                ),
                reset_password_token_secret=self._secret + "_reset",
                verification_token_secret=self._secret + "_verify",
            )

    def add_auth_routes_to(
        self, router: APIRouter, user_read_schema: Any, user_create_schema: Any
    ) -> None:
        fastapi_users = self._fastapi_users

        router.include_router(
            fastapi_users.get_auth_router(backend=self._auth_backend),  # type: ignore
        )
        router.include_router(
            fastapi_users.get_register_router(
                user_schema=user_read_schema,
                user_create_schema=user_create_schema,
            ),
        )
        router.include_router(fastapi_users.get_reset_password_router())
        router.include_router(fastapi_users.get_verify_router(user_read_schema))

    def add_user_routes_to(
        self, router: APIRouter, user_read_schema: Any, user_update_schema: Any
    ) -> None:
        router.include_router(
            self._fastapi_users.get_users_router(
                user_schema=user_read_schema,
                user_update_schema=user_update_schema,
            ),
        )

    def current_user(
        self, active: bool = False, verified: bool = False, superuser: bool = False
    ) -> Callable[[], User]:
        return self._fastapi_users.current_user(  # type: ignore
            active=active, verified=verified, superuser=superuser
        )
