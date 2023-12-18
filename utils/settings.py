from pathlib import Path
from sys import path

from pydantic.fields import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(path[0]) / ".env", env_file_encoding="utf-8", extra="ignore"
    )

    debug: bool = False

    db_url: str = Field(default_factory=str)
    cache_url: str = Field(default_factory=str)
    cache_ttl: int = 60 * 60 * 24  # 1 day
    secret_key: str = "secret_key"
    openapi_token_url: str = "/auth/login"
    google_api_key: str = Field(default_factory=str)
