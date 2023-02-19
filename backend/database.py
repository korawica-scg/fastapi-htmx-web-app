from typing import Any
import logging
from typing import AsyncIterator
from fastapi import Depends
from sqlalchemy import MetaData, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from .config import settings

logger = logging.getLogger(__name__)

engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URL,
    echo=settings.SQLALCHEMY_ECHO_SQL,
    connect_args={
        # This is needed only for SQLite. It's not needed for other databases.
        # By this example, it use SQLite because it uses a single file and Python
        # has integrated support. But in FastAPI, using normal functions (def)
        # more than one thread could interact with the database for the same
        # request, so we need to make SQLite know that it should allow that with,
        # docs: https://fastapi.tiangolo.com/tutorial/sql-databases/
        "check_same_thread": False
    }
)
SessionLocal = sessionmaker(
    bind=engine, autoflush=False, autocommit=False, future=True
)

async_engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_ASYNC_URL,
    echo=settings.SQLALCHEMY_ECHO_SQL,
    pool_pre_ping=True,
    connect_args={
        # This is needed only for SQLite. It's not needed for other databases.
        # By this example, it use SQLite because it uses a single file and Python
        # has integrated support. But in FastAPI, using normal functions (def)
        # more than one thread could interact with the database for the same
        # request, so we need to make SQLite know that it should allow that with,
        # docs: https://fastapi.tiangolo.com/tutorial/sql-databases/
        "check_same_thread": False
    }
)
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine, autoflush=False, autocommit=False,
    # The "future" flag is a mechanism to allow a seamless shift from prior versions
    # of SQLAlchemy to the new v2.0. The interim version (v1.4) has a foot on each
    # side of the transition.
    # docs: https://docs.sqlalchemy.org/en/14/tutorial/index.html
    future=True,
    expire_on_commit=False
)

# Explicitly setting the indexes' namings according to your
# database's convention is preferable over sqlalchemy's.
# docs: https://github.com/zhanymkanov/fastapi-best-practices#11-sqlalchemy-set-db-keys-naming-convention
POSTGRES_INDEXES_NAMING_CONVENTION = {
    "ix": "%(column_0_label)s_idx",
    "uq": "%(table_name)s_%(column_0_name)s_key",
    "ck": "%(table_name)s_%(constraint_name)s_check",
    "fk": "%(table_name)s_%(column_0_name)s_fkey",
    "pk": "%(table_name)s_pkey",
}
metadata = MetaData(
    naming_convention=POSTGRES_INDEXES_NAMING_CONVENTION,
    # In SQLite schema, the value should be `main` only because it does not implement with
    # schema system.
    schema='main'
)
Base = declarative_base(metadata=metadata)


# @as_declarative()
# class Base:
#     id: Any
#     __name__: str
#
#     # Generate __tablename__ automatically
#     @declared_attr
#     def __tablename__(cls) -> str:
#         return cls.__name__.lower()


class CustomBase(Base):
    __abstract__ = True

    def __repr__(self) -> str:
        columns = ", ".join(
            [f"{k}={repr(v)}" for k, v in self.__dict__.items() if not k.startswith("_")]
        )
        return f"<{self.__class__.__name__}({columns})>"


async def get_session():
    """Get database session with synchronous"""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


async def get_async_session() -> AsyncIterator[sessionmaker]:
    """Get database session with asynchronous"""
    try:
        yield AsyncSessionLocal
    except SQLAlchemyError as err:
        logger.error(err)
    finally:
        # await async_engine.dispose()
        ...


class BaseCRUD:
    def __init__(self, session: sessionmaker = Depends(get_async_session)) -> None:
        self.async_session = session


# def init_db():
#     # Tables should be created with Alembic migrations. But if you don't want to use migrations,
#     # create the tables un-commenting the next line
#     # Base.metadata.create_all(bind=engine)
#
#     user = get_user_by_email(db, email=settings.FIRST_SUPERUSER)
#     if not user:
#         user_in = UserCreate(
#             email=settings.FIRST_SUPERUSER,
#             password=settings.FIRST_SUPERUSER_PASSWORD,
#             is_superuser=True,
#         )
#         user = create(db, obj_in=user_in)
