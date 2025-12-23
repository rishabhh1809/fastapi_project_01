from pathlib import Path
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class CommonSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).parents[1] / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


# --------------------------------------------------------------- APP ---------------------------------------------------------------
class AppSettings(CommonSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).parents[1] / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_prefix="",
    )

    api_version: str = "1.0.0"
    project_name: str = Field(default="Event Ticketing Platform", alias="PROJECT_NAME")
    project_domain: str = Field(default="localhost", alias="PROJECT_DOMAIN")
    debug: bool = Field(default=False, alias="DEBUG")


# -------------------------------------------------------------- SECURITY ----------------------------------------------------------
class SecuritySettings(CommonSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).parents[1] / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_prefix="",
    )

    jwt_secret: str = Field(
        default="your-super-secret-key-change-in-production", alias="JWT_SECRET"
    )
    jwt_algorithm: str = Field(default="HS384")
    access_token_expire_minutes: int = Field(
        default=30, alias="ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    refresh_token_expire_days: int = Field(default=7, alias="REFRESH_TOKEN_EXPIRE_DAYS")


# --------------------------------------------------------------- CORS --------------------------------------------------------------
class CORSSettings(CommonSettings):
    allowed_origins: list[str] = Field(default=["*"])
    allowed_methods: list[str] = Field(default=["*"])
    allowed_headers: list[str] = Field(default=["*"])


# --------------------------------------------------------------- REDIS ---------------------------------------------------------
class RedisSettings(CommonSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).parents[1] / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_prefix="",
    )

    redis_host: str = Field(default="localhost", alias="REDIS_HOST")
    redis_port: int = Field(default=6379, alias="REDIS_PORT")
    redis_password: str = Field(default="", alias="REDIS_PASSWORD")
    redis_db: int = Field(default=0, alias="REDIS_DB")

    @property
    def redis_url(self) -> str:
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"


# -------------------------------------------------------------- DATABASE ----------------------------------------------------------
class DatabaseSettings(CommonSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).parents[1] / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_prefix="",
    )

    # Primary DB
    db_user: str = Field(default="postgres", alias="DB_USER")
    db_password: str = Field(default="postgres", alias="DB_PASSWORD")
    db_host: str = Field(default="localhost", alias="DB_HOST")
    db_port: str = Field(default="5432", alias="DB_PORT")
    db_name: str = Field(default="event_ticketing", alias="DB_NAME")

    # Connection pool settings
    db_echo: bool = Field(default=False, alias="DB_ECHO")
    db_pool_size: int = Field(default=10, alias="DB_POOL_SIZE")
    db_max_overflow: int = Field(default=20, alias="DB_MAX_OVERFLOW")

    @property
    def db_url(self) -> str:
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    @property
    def db_url_sync(self) -> str:
        return f"postgresql+psycopg2://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"


# --------------------------------------------------------------- MASTER SETTINGS ---------------------------------------------------
class Settings(CommonSettings):
    app: AppSettings = Field(default_factory=AppSettings)
    db: DatabaseSettings = Field(default_factory=DatabaseSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    cors: CORSSettings = Field(default_factory=CORSSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
