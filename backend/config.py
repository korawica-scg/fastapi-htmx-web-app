import os
import logging
import secrets
import pathlib
from typing import Dict, List, Union, Optional, Any
from pydantic import (
    BaseSettings,
    AnyHttpUrl,
    validator,
    PostgresDsn,
    EmailStr,
    HttpUrl,
)
from dotenv import load_dotenv
from functools import lru_cache

load_dotenv(dotenv_path='../.env')


# docs: https://docs.pydantic.dev/usage/settings/
class Settings(BaseSettings):
    """
    usages:
        ..> settings = Settings()
        ... settings.API_V1_STR
    """
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)

    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    SERVER_NAME: str
    SERVER_HOST: AnyHttpUrl

    # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    # e.g: '["http://localhost", "http://localhost:4200", "http://localhost:3000", \
    # "http://localhost:8080", "http://local.dockertoolbox.tiangolo.com"]'
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    PROJECT_NAME: str
    SENTRY_DSN: Optional[HttpUrl] = None

    @validator("SENTRY_DSN", pre=True)
    def sentry_dsn_can_be_blank(cls, v: str) -> Optional[str]:
        return v or None

    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )

    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[EmailStr] = None
    EMAILS_FROM_NAME: Optional[str] = None

    @validator("EMAILS_FROM_NAME")
    def get_project_name(cls, v: Optional[str], values: Dict[str, Any]) -> str:
        return v or values["PROJECT_NAME"]

    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48
    EMAIL_TEMPLATES_DIR: str = "/app/app/email-templates/build"
    EMAILS_ENABLED: bool = False

    @validator("EMAILS_ENABLED", pre=True)
    def get_emails_enabled(cls, _: bool, values: Dict[str, Any]) -> bool:
        return bool(
            values.get("SMTP_HOST")
            and values.get("SMTP_PORT")
            and values.get("EMAILS_FROM_EMAIL")
        )

    EMAIL_TEST_USER: EmailStr = "test@example.com"  # type: ignore
    FIRST_SUPERUSER: EmailStr
    FIRST_SUPERUSER_PASSWORD: str
    USERS_OPEN_REGISTRATION: bool = False

    class Config:
        # # For get configuration from `.env` file.
        # env = os.environ["APP_ENV"]
        # env_file = pathlib.Path(__file__).parent.parent / ".env"
        case_sensitive = True


class BaseConfig:
    BASE_DIR: pathlib.Path = pathlib.Path(__file__).parent.parent
    APP_VERSION: int = 1
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = ['http://localhost:8000']

    # Security Configuration
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8

    # SQLAlchemy Configuration
    SQLALCHEMY_DATABASE_URL: str = os.environ.get("DATABASE_URL", f"sqlite:///{BASE_DIR}/db.sqlite3")
    SQLALCHEMY_DATABASE_ASYNC_URL: str = os.environ.get("DATABASE_URL", f"sqlite+aiosqlite:///{BASE_DIR}/db.sqlite3")
    SQLALCHEMY_DATABASE_CONNECT_DICT: dict = {}
    SQLALCHEMY_ECHO_SQL: bool = False

    # Logging Configuration
    LOGGING_LEVEL: str = logging.DEBUG
    LOGGING_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOGGING_CONF: dict = {
        # mandatory field
        "version": 1,
        # if you want to overwrite existing loggers' configs
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "()": "uvicorn.logging.DefaultFormatter",
                "fmt": "%(levelprefix)s %(asctime)s %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "basic": {
                "format": LOGGING_FORMAT,
            }
        },
        "handlers": {
            "console": {
                "formatter": "basic",
                "class": "logging.StreamHandler",
                # "stream": "ext://sys.stderr",
                "stream": "ext://sys.stdout",
                "level": LOGGING_LEVEL,
            }
        },
        "loggers": {
            "simple_example": {
                "handlers": ["console"],
                "level": LOGGING_LEVEL,
                # "propagate": False
            }
        },
    }

    # Email
    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48


class DevelopmentConfig(BaseConfig):
    pass


class ProductionConfig(BaseConfig):
    pass


class TestingConfig(BaseConfig):
    pass


@lru_cache()
def get_settings():
    config_cls_dict: dict = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
        "testing": TestingConfig
    }
    config_name = os.environ.get("APP_ENV", "development")
    config_cls = config_cls_dict[config_name]
    return config_cls()


settings: BaseConfig = get_settings()
