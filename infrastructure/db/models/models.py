from datetime import datetime

from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from fastapi_users_db_sqlalchemy import UUID_ID
from fastapi_users_db_sqlalchemy.generics import GUID
from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import DeclarativeBase, mapped_column, relationship
from sqlalchemy.orm.base import Mapped
from sqlalchemy.sql.sqltypes import TIMESTAMP

from infrastructure.uuid import UUID


class Base(DeclarativeBase):
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class User(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = "users"

    id: Mapped[UUID_ID] = mapped_column(GUID, primary_key=True, default=UUID.generate)

    name: Mapped[str] = mapped_column()
    contact: Mapped[str] = mapped_column()
    permissions: Mapped[int] = mapped_column()
    membership_date: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))


class Book(Base):
    __tablename__ = "books"

    id: Mapped[UUID_ID] = mapped_column(GUID, primary_key=True, default=UUID.generate)
    isbn: Mapped[str] = mapped_column()
    title: Mapped[str] = mapped_column()
    category: Mapped[str] = mapped_column()
    language: Mapped[str] = mapped_column()
    pub_date: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))

    authors: Mapped[list["Author"]] = relationship(
        secondary="authors_books", back_populates="books", lazy="selectin"
    )


class Author(Base):
    __tablename__ = "authors"

    id: Mapped[UUID_ID] = mapped_column(GUID, primary_key=True, default=UUID.generate)
    name: Mapped[str] = mapped_column()

    books: Mapped[list["Book"]] = relationship(
        secondary="authors_books", back_populates="authors", lazy="selectin"
    )


class AuthorsBooks(Base):
    __tablename__ = "authors_books"

    author_id: Mapped[UUID_ID] = mapped_column(
        ForeignKey("authors.id", ondelete="CASCADE"),
        primary_key=True,
    )
    book_id: Mapped[UUID_ID] = mapped_column(
        ForeignKey("books.id", ondelete="CASCADE"),
        primary_key=True,
    )
