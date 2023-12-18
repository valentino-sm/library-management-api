from fastapi import APIRouter

from presentation.asgi.fastapi.abc_router import ABCRouterBuilder
from presentation.asgi.fastapi.auth import ABCAuthService
from presentation.asgi.requests.user import UserRead, UserUpdate
from utils.logging import Logging


class UserRouterBuilder(ABCRouterBuilder):
    def __init__(
        self,
        logging: Logging,
        auth_service: ABCAuthService,
    ) -> None:
        self._logger = logging.get_logger(__name__)
        self._auth_service = auth_service

    def create_router(self) -> APIRouter:
        router = APIRouter(prefix="/users", tags=["users"])
        self._auth_service.add_user_routes_to(router, UserRead, UserUpdate)

        return router
