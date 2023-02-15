import os
import pathlib
from dotenv import load_dotenv
from functools import lru_cache

load_dotenv(dotenv_path='../.env')


# https://docs.pydantic.dev/usage/settings/
class Setting:
    ...


class BaseConfig:
    BASE_DIR: pathlib.Path = pathlib.Path(__file__).parent.parent
    SQLALCHEMY_DATABASE_URL: str = os.environ.get("DATABASE_URL", f"sqlite:///{BASE_DIR}/db.sqlite3")
    SQLALCHEMY_DATABASE_ASYNC_URL: str = os.environ.get("DATABASE_URL", f"sqlite+aiosqlite:///{BASE_DIR}/db.sqlite3")
    SQLALCHEMY_ECHO_SQL: bool = False
    SQLALCHEMY_DATABASE_CONNECT_DICT: dict = {}


class DevelopmentConfig(BaseConfig):
    pass


class ProductionConfig(BaseConfig):
    pass


class TestingConfig(BaseConfig):
    pass


@lru_cache()
def get_settings():
    config_cls_dict = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
        "testing": TestingConfig
    }
    config_name = os.environ.get("FASTAPI_ENV", "development")
    config_cls = config_cls_dict[config_name]
    return config_cls()


settings = get_settings()
