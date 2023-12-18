from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Security

from core.models.user import User
from core.services.book import BookService
from presentation.asgi.fastapi.abc_router import ABCRouterBuilder
from presentation.asgi.fastapi.auth import ABCAuthService
from presentation.asgi.responses.base import BaseResponse
from utils.logging import Logging


class BookRouterBuilder(ABCRouterBuilder):
    def __init__(
        self,
        logging: Logging,
        auth_service: ABCAuthService,
        book_service: BookService,
    ) -> None:
        self._logger = logging.get_logger(__name__)
        self._auth_service = auth_service
        self._book_service = book_service

    def create_router(self) -> APIRouter:
        router = APIRouter(prefix="/books", tags=["books"])
        router.responses.update({
            400: {"model": BaseResponse},
            500: {"model": BaseResponse},
        })

        @router.get("/fetch_by_id")
        async def _(
            _: Annotated[User, Security(self._auth_service.current_user(active=True))],
            book_id: str,
        ):
            """
            Get book by Google Books ID and write it to the database.
            """
            return await self._book_service.fetch_by_id(book_id)

        @router.get("/fetch_by_isbn")
        async def _(
            _: Annotated[User, Security(self._auth_service.current_user(active=True))],
            book_isbn: str,
        ):
            """
            Get book by ISBN and write it to the database.
            """
            return await self._book_service.fetch_by_isbn(book_isbn)

        @router.get("/fetch_by_category")
        async def _(
            _: Annotated[User, Security(self._auth_service.current_user(active=True))],
            category: str,
        ):
            """
            Get book by category and write it to the database.
            """
            return await self._book_service.fetch_by_category(category)

        @router.get("/{book_id}")
        async def _(
            _: Annotated[User, Security(self._auth_service.current_user(active=True))],
            book_id: UUID,
        ):
            """
            Get book by internal ID.
            """
            return await self._book_service.get_by_id(book_id)

        @router.post(path="")
        async def _(
            _: Annotated[User, Security(self._auth_service.current_user(active=True))],
            title: str | None = None,
            author: str | None = None,
            pub_date: datetime | None = None,
            isbn: str | None = None,
        ):
            """
            Search for books.
            """
            return await self._book_service.search(
                title=title, author=author, isbn=isbn
            )

        return router
