from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Room Management API"
    environment: str = "local"
    database_url: str = "postgresql+psycopg://room_manage:room_manage@db:5432/room_manage"
    secret_key: str = "change-this-local-secret"
    access_token_expire_minutes: int = 60 * 12
    access_token_cookie_name: str = "access_token"
    cookie_secure: bool = False
    password_hash_rounds: int = 12
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="ROOM_MANAGE_",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
