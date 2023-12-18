from typing import Any, Sequence
from uuid import UUID

from core.models.book import Book
from infrastructure.db.abc_repository import BaseRepository
from infrastructure.db.models.models import Author as AuthorModel
from infrastructure.db.models.models import Book as BookModel
from infrastructure.db.session_manager import ABCSessionManager
from utils.logging import Logging


class BookRepository:
    def __init__(
        self,
        logging: Logging,
        repository: BaseRepository,  # type: ignore - hack for DI
        session_manager: ABCSessionManager,
    ) -> None:
        self._logger = logging.get_logger(__name__)
        self._repository: BaseRepository[BookModel] = repository
        self._session_manager = session_manager

    async def create_book(self, book: Book) -> BookModel:
        book_model = BookModel(
            **book.dict(exclude={"authors"}),
            authors=[
                await self._repository.create_obj(AuthorModel(name=author.name))  # type: ignore
                for author in book.authors
            ],
        )
        return await self._repository.create_obj(book_model)

    async def get_book_by_id(self, id_: UUID) -> BookModel:
        return await self._repository.get_by_id(BookModel, id_)

    async def filter_by(self, **kwargs: Any) -> Sequence[BookModel]:
        return await self._repository.filter_by(BookModel, **kwargs)

    async def search(self, **kwargs: Any) -> Sequence[BookModel]:
        return await self._repository.search_by(BookModel, **kwargs)
