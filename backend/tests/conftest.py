from typing import AsyncGenerator, Generator
import pytest
from httpx import AsyncClient
from sqlalchemy import create_engine, event
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from backend.database import get_session
from backend.app import create_app
from backend.database import Base
from backend.config import settings


@pytest.fixture
async def ac() -> AsyncGenerator:
    async with AsyncClient(app=create_app(), base_url="https://test") as c:
        yield c


@pytest.fixture(scope="session")
def setup_db() -> Generator:
    engine = create_engine(f"{settings.SQLALCHEMY_DATABASE_ASYNC_URL.replace('+asyncpg', '')}")
    conn = engine.connect()
    conn.execute("commit")
    try:
        conn.execute("drop database test")
    except SQLAlchemyError:
        pass
    finally:
        conn.close()

    conn = engine.connect()
    conn.execute("commit")
    conn.execute("create database test")
    conn.close()

    yield

    conn = engine.connect()
    conn.execute("commit")
    try:
        conn.execute("drop database test")
    except SQLAlchemyError:
        pass
    conn.close()


@pytest.fixture(scope="session", autouse=True)
def setup_test_db(setup_db):
    engine = create_engine(f"{settings.SQLALCHEMY_DATABASE_ASYNC_URL.replace('+asyncpg', '')}/test")

    with engine.begin():
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
        yield
        Base.metadata.drop_all(engine)


@pytest.fixture
async def session():
    # https://github.com/sqlalchemy/sqlalchemy/issues/5811#issuecomment-756269881
    async_engine = create_async_engine(f"{settings.SQLALCHEMY_DATABASE_ASYNC_URL}/test")
    async with async_engine.connect() as conn:

        await conn.begin()
        await conn.begin_nested()
        AsyncSessionLocal = async_sessionmaker(
            bind=conn,
            autocommit=False,
            autoflush=False,
            future=True
        )

        async_session = AsyncSessionLocal()

        @event.listens_for(async_session.sync_session, "after_transaction_end")
        def end_savepoint(session, transaction):
            if conn.closed:
                return
            if not conn.in_nested_transaction:
                conn.sync_connection.begin_nested()

        def test_get_session() -> Generator:
            try:
                yield AsyncSessionLocal
            except SQLAlchemyError:
                pass

        create_app().dependency_overrides[get_session] = test_get_session

        yield async_session
        await async_session.close()
        await conn.rollback()
