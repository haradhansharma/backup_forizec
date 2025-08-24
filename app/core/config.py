# app/core/config.py
# This file contains the configuration settings for the Forizec application.

from pathlib import Path

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # app/core/config.py is 3 levels deep


class Settings(BaseSettings):
    ENV: str = "dev"  # dev | staging | prod
    DEBUG: bool = True
    DB_BACKEND: str = "sqlite"  # sqlite | mysql | postgresql

    # Shared
    DB_HOST: str | None = None
    DB_PORT: int | None = None
    DB_USER: str | None = None
    DB_PASSWORD: str | None = None
    DB_NAME: str | None = None

    DB_PATH: str = "./data/forizec.db"  # sqlite path

    # Optional one-shot override
    DATABASE_URL: str | None = None

    SECRET_KEY: str = "8f98e3609c5def7af9519661a25881125c769bc91e489e0f30c675bed209f4aa"

    PROJECT_NAME: str = "Forizec"
    PROJECT_VERSION: str = "1.0.0"
    PROJECT_DESCRIPTION: str = "Forizec - A FastAPI Project"
    API_V1_STR: str = "/api/v1"
    BASE_DIR: Path = BASE_DIR
    STATIC_DIR: Path = BASE_DIR / "static"
    MEDIA_DIR: Path = BASE_DIR / "media"
    TEMPLATES_DIR: Path = BASE_DIR / "templates"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @computed_field
    @property
    def EFFECTIVE_DATABASE_URL(self) -> str:
        # If supplied DATABASE_URL directly, prefer it.
        if self.DATABASE_URL:
            return self.DATABASE_URL

        if self.DB_BACKEND == "sqlite":
            return f"sqlite+aiosqlite:///{self.DB_PATH}"
        elif self.DB_BACKEND == "mysql":
            # allow empty password safely
            pw = self.DB_PASSWORD or ""
            return (
                f"mysql+asyncmy://{self.DB_USER}:{pw}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            )
        elif self.DB_BACKEND in ("postgresql", "postgres"):
            pw = self.DB_PASSWORD or ""
            return f"postgresql+asyncpg://{self.DB_USER}:{pw}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        raise ValueError(f"Unsupported DB_BACKEND: {self.DB_BACKEND}")


settings = Settings()  # type: ignore
