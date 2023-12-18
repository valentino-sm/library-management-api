from functools import cached_property, wraps
from typing import (Any, Awaitable, Callable, Coroutine, ParamSpec, Protocol,
                    TypeVar)
from urllib.parse import urlparse

from aiocache import BaseCache  # type: ignore
from aiocache import cached as aiocache_cached  # type: ignore
from aiocache import caches as aiocache_caches  # type: ignore
from aiocache.lock import RedLock  # type: ignore

from utils.logging import Logging

T = TypeVar("T")
P = ParamSpec("P")
_A = Awaitable
_C = Callable
_G = Coroutine


class ABCCaches(Protocol):
    @property
    def lock(self) -> type[RedLock]: ...

    @cached_property
    def memory(self) -> BaseCache: ...

    def memory_decorator(self, func: _C[P, _A[T]]) -> _C[P, _G[Any, Any, T]]: ...

    @cached_property
    def distributed(self) -> BaseCache: ...

    def distributed_decorator(self, func: _C[P, _A[T]]) -> _C[P, _G[Any, Any, T]]: ...


class Caches(ABCCaches):
    def __init__(self, logging: Logging, url: str, ttl: int) -> None:
        self._logger = logging.get_logger(__name__)
        url_parsed = urlparse(url)
        self._ttl = ttl

        _scheme = url_parsed.scheme
        _provider = _scheme[0].upper() + _scheme[1:]
        _config_for_memory = {
            "cache": "aiocache.SimpleMemoryCache",
        }
        _config_for_distributed = (
            {
                "cache": f"aiocache.{_provider}Cache",
                "endpoint": url_parsed.hostname,
                "port": url_parsed.port,
                "db": url_parsed.path.strip("/"),
                "password": url_parsed.password,
                "serializer": {"class": "aiocache.serializers.PickleSerializer"},
            }
            if _provider not in ("", "Memory", "NoCache")
            else _config_for_memory
        )
        aiocache_caches.set_config({  # type: ignore
            "default": _config_for_memory,
            "distributed": _config_for_distributed,
        })

        self._memory: BaseCache = aiocache_caches.get("default")  # type: ignore
        self._distributed: BaseCache = aiocache_caches.get("distributed")  # type: ignore

    @property
    def lock(self) -> type[RedLock]:
        return RedLock

    @cached_property
    def memory(self) -> BaseCache:
        return self._memory

    @cached_property
    def distributed(self) -> BaseCache:
        return self._distributed

    def _decorator(self, func: _C[P, _A[T]], alias: str) -> _C[P, _G[Any, Any, T]]:
        aiocache_func = aiocache_cached(  # type: ignore
            alias=alias,
            ttl=self._ttl,
        )(func)

        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            return await aiocache_func(*args, **kwargs)  # type: ignore

        return wrapper

    def distributed_decorator(self, func: _C[P, _A[T]]) -> _C[P, _G[Any, Any, T]]:
        return self._decorator(func, "distributed")

    def memory_decorator(self, func: _C[P, _A[T]]) -> _C[P, _G[Any, Any, T]]:
        return self._decorator(func, "default")


# class NoCache(BaseCache):
#     async def _get(self, *args, **kwargs):  # pyright: ignore
#         return None
#
#     async def _set(self, *args, **kwargs):  # pyright: ignore
#         return True
#
#     async def _exists(self, *args, **kwargs):  # pyright: ignore
#         return False
#
#     # For Lock
#     async def _add(self, *args, **kwargs):  # pyright: ignore
#         return None
#
#     async def _redlock_release(self, *args, **kwargs):  # pyright: ignore
#         return None
