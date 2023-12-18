from datetime import datetime

from pydantic import BaseModel


class Book(BaseModel):
    isbn: str
    title: str
    category: str
    language: str
    pub_date: datetime

    authors: list["Author"]


class Author(BaseModel):
    name: str
