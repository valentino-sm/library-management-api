import uuid

from fastapi_users.db.base import BaseUserDatabase
from fastapi_users.manager import BaseUserManager, UUIDIDMixin
from starlette.requests import Request
from starlette.responses import Response

from infrastructure.db.models.models import User


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    def __init__(
        self,
        user_db: BaseUserDatabase[User, uuid.UUID],
        reset_password_token_secret: str,
        verification_token_secret: str,
    ):
        super().__init__(user_db)
        self.reset_password_token_secret = reset_password_token_secret
        self.verification_token_secret = verification_token_secret

    async def on_after_login(
        self,
        user: User,
        request: Request | None = None,
        response: Response | None = None,
    ) -> None:
        print(f"User {user.id} logged in.")

    async def on_after_logout(self, user: User, request: Request | None = None):
        print(f"User {user.id} logged out.")

    async def on_after_register(self, user: User, request: Request | None = None):
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Request | None = None
    ):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: User, token: str, request: Request | None = None
    ):
        print(f"Verification requested for user {user.id}. Verification token: {token}")
