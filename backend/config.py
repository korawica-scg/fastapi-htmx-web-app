import logging
import os
import pathlib
from typing import Dict
from pydantic import BaseSettings
from dotenv import load_dotenv
from functools import lru_cache

load_dotenv(dotenv_path='../.env')


# https://docs.pydantic.dev/usage/settings/
class Settings(BaseSettings):
    """
    usages:
        ..> Settings().APP_ENV
    """
    APP_ENV: str

    class Config:
        # env = os.environ["APP_ENV"]
        env_file = pathlib.Path(__file__).parent.parent / ".env"
        case_sensitive = True


class BaseConfig:
    BASE_DIR: pathlib.Path = pathlib.Path(__file__).parent.parent
    APP_VERSION: int = 1

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
