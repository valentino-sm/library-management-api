from fastapi import APIRouter

from presentation.asgi.fastapi.abc_router import ABCRouterBuilder
from presentation.asgi.fastapi.auth import ABCAuthService
from presentation.asgi.requests.user import UserCreate, UserRead
from utils.logging import Logging


class AuthRouterBuilder(ABCRouterBuilder):
    def __init__(
        self,
        logging: Logging,
        auth_service: ABCAuthService,
    ) -> None:
        self._logger = logging.get_logger(__name__)
        self._auth_service = auth_service

    def create_router(self) -> APIRouter:
        router = APIRouter(prefix="/auth", tags=["auth"])
        self._auth_service.add_auth_routes_to(router, UserRead, UserCreate)

        return router
