from core.services.book import BookService
from core.services.books_source import ABCBooksSource, GoogleBooksSource
from infrastructure.caches import ABCCaches, Caches
from infrastructure.container import Container
from infrastructure.db.abc_repository import BaseRepository
from infrastructure.db.engine import ABCDatabaseEngine
from infrastructure.db.repositories.book import BookRepository
from infrastructure.db.session_manager import ABCSessionManager, SessionManager
from infrastructure.db.sqlalchemy.engine import SQLAlchemyEngine
from infrastructure.db.sqlalchemy.repository import SQLAlchemyRepository
from infrastructure.db.unitofwork import ABCUnitOfWork, SQLAlchemyUnitOfWork
from infrastructure.http import ABCHTTPClient, HTTPXClient
from infrastructure.lifespan import ABCLifespan, EmptyLifespan
from presentation.asgi.abc_builder import ASGIApp, ASGIAppBuilder
from presentation.asgi.fastapi.abc_router import ABCRouterBuilder
from presentation.asgi.fastapi.auth import ABCAuthService, FastAPIUsersService
from presentation.asgi.fastapi.builder import FastAPIAppBuilder
from presentation.asgi.routes.auth import AuthRouterBuilder
from presentation.asgi.routes.book import BookRouterBuilder
from presentation.asgi.routes.user import UserRouterBuilder
from utils.logging import Logging
from utils.settings import Settings


def build_container() -> Container:
    settings = Settings()

    logging = Logging(is_debug=settings.debug)
    logger = logging.get_logger(__name__)
    logger.info("Starting building container")

    container = Container()

    # INFRASTRUCTURE
    container.register(Logging, instance=logging)
    container.register(ABCLifespan, EmptyLifespan)
    container.register(ABCHTTPClient, HTTPXClient)
    container.register(
        ABCBooksSource, GoogleBooksSource, api_key=settings.google_api_key
    )
    container.register(
        ABCCaches, Caches, url=settings.cache_url, ttl=settings.cache_ttl
    )

    # SERVICES
    container.register(BookService)

    # REPOSITORIES
    container.register(BookRepository)

    # DATABASE
    container.register(BaseRepository, SQLAlchemyRepository)
    container.register(ABCUnitOfWork, SQLAlchemyUnitOfWork)
    container.register(ABCSessionManager, SessionManager)
    container.register(ABCDatabaseEngine, SQLAlchemyEngine, url=settings.db_url)

    # ROUTES
    container.register(ABCRouterBuilder, AuthRouterBuilder)
    container.register(ABCRouterBuilder, UserRouterBuilder)
    container.register(ABCRouterBuilder, BookRouterBuilder)

    # ASGI App
    container.register(
        ABCAuthService,
        FastAPIUsersService,
        secret=settings.secret_key,
        token_url=settings.openapi_token_url,
    )
    container.register(ASGIAppBuilder, FastAPIAppBuilder)
    return container


def create_app() -> ASGIApp:
    container = build_container()
    app_builder: ASGIAppBuilder = container.resolve(ASGIAppBuilder)
    return app_builder.create_app()
