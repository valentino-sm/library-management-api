from datetime import datetime
from typing import Any, Protocol

import pytz

from core.models.book import Author, Book
from infrastructure.caches import ABCCaches
from infrastructure.http import ABCHTTPClient
from utils.exceptions import ExternalValueError
from utils.logging import Logging


class ABCBooksSource(Protocol):
    async def get_book_by_id(self, id_: str) -> Book:
        raise NotImplementedError

    async def search_books(self, query: str) -> list[Book]:
        raise NotImplementedError

    async def get_books_by_isbn(self, isbn: str) -> list[Book]:
        raise NotImplementedError

    async def get_books_by_category(self, category: str) -> list[Book]:
        raise NotImplementedError


class GoogleBooksSource(ABCBooksSource):
    def __init__(
        self,
        logging: Logging,
        http_client: ABCHTTPClient,
        caches: ABCCaches,
        api_key: str,
    ) -> None:
        self._logger = logging.get_logger(__name__)
        self._http_client = http_client

        self._api_url = "https://www.googleapis.com/books/v1/volumes"
        self._api_params = {"key": api_key}

        self.get_book_by_id = caches.distributed_decorator(
            self.get_book_by_id,
        )
        self.search_books = caches.distributed_decorator(
            self.search_books,
        )

    @classmethod
    def _from_dict(cls, data: dict[str, Any]) -> Book:
        isbn = [
            isbn["identifier"]
            for isbn in data["industryIdentifiers"]
            if isbn["type"] == "ISBN_10"
        ][0]
        try:
            pub_date = datetime.fromisoformat(data["publishedDate"])
        except ValueError:
            pub_date = datetime.fromisocalendar(
                year=int(data["publishedDate"]),
                week=1,
                day=1,
            )
            pub_date.replace(tzinfo=pytz.utc)
        return Book(
            isbn=isbn,
            title=data["title"],
            category=data["categories"][0],
            language=data["language"],
            pub_date=pub_date,
            authors=[Author(name=author) for author in data["authors"]],
        )

    async def get_book_by_id(self, id_: str) -> Book:
        self._logger.debug(f"Cache is empty. Fetching book by id: {id_}")
        response = await self._http_client.get(
            url=f"{self._api_url}/{id_}",
            params=self._api_params,
        )
        if "error" in response:
            raise ExternalValueError(response["error"]["message"])
        try:
            return self._from_dict(response["volumeInfo"])
        except (KeyError, IndexError, ValueError):
            raise ExternalValueError("No book found") from None

    async def search_books(self, query: str) -> list[Book]:
        self._logger.debug(f"Cache is empty. Fetching books by query: {query}")
        response = await self._http_client.get(
            url=self._api_url,
            params={**self._api_params, "q": query},
        )
        if "error" in response:
            raise ExternalValueError(response["error"]["message"])
        # self._logger.debug(response)
        books: list[Book] = []
        for book in response["items"]:
            try:
                books.append(self._from_dict(book["volumeInfo"]))
            except (KeyError, IndexError, ValueError):
                pass
                # self._logger.debug(f"Error: {e} with book: {book}")
        if not books:
            raise ExternalValueError("No books found") from None
        return books

    async def get_books_by_isbn(self, isbn: str) -> list[Book]:
        return await self.search_books(f"isbn:{isbn}")

    async def get_books_by_category(self, category: str) -> list[Book]:
        return await self.search_books(f"subject:{category}")
