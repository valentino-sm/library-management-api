from typing import Any
from uuid import UUID

from core.models.book import Book
from core.services.books_source import ABCBooksSource
from infrastructure.db.exceptions import exc
from infrastructure.db.repositories.book import BookRepository
from infrastructure.db.session_manager import ABCSessionManager
from utils.exceptions import AppError
from utils.logging import Logging


class BookService:
    def __init__(
        self,
        logging: Logging,
        book_repository: BookRepository,
        session_manager: ABCSessionManager,
        books_source: ABCBooksSource,
    ):
        self._logger = logging.get_logger(__name__)
        self._book_repository = book_repository
        self._session_manager = session_manager
        self._books_source = books_source

    async def _create_if_not_exists(self, book: Book):
        try:
            books = await self._book_repository.filter_by(
                isbn=book.isbn, title=book.title
            )
            return books[0]
        except (exc.NoResultFound, IndexError):
            self._logger.debug(f"Creating book {book}")
            return await self._book_repository.create_book(book)

    async def get_by_id(self, id_: UUID):
        async with self._session_manager.make_session():
            try:
                return await self._book_repository.get_book_by_id(id_)
            except exc.NoResultFound:
                raise AppError("Book not found") from None

    async def fetch_by_id(self, id_: str):
        book = await self._books_source.get_book_by_id(id_)
        async with self._session_manager.make_session():
            return await self._create_if_not_exists(book)

    async def fetch_by_isbn(self, isbn: str):
        books = await self._books_source.get_books_by_isbn(isbn)
        async with self._session_manager.make_session():
            return [await self._create_if_not_exists(book) for book in books]

    async def fetch_by_category(self, category: str):
        books = await self._books_source.get_books_by_category(category)
        async with self._session_manager.make_session():
            books = [await self._create_if_not_exists(book) for book in books]
            self._logger.debug([book.isbn for book in books])
            return books

    async def search(self, **kwargs: Any):
        async with self._session_manager.make_session():
            return await self._book_repository.search(**kwargs)
