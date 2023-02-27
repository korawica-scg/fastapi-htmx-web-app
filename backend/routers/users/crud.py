from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncIterator, Union, Type, List, Optional
from .models import User
from ...database import get_async_session
from ...database import BaseCRUD
from ...securities import get_password_hash
from ...securities import verify_password
from .schemas import User as SchemaUser
from .schemas import UserCreate as SchemaUserCreate
from .schemas import UserUpdate as SchemaUserUpdate
from .schemas import UserCreateForm as SchemaUserCreateForm

"""
the Synchronous CRUD functions for get any models from database.
"""


def get_user(session: Session, user_id: int) -> Optional[User]:
    return session.query(User).filter(User.id == user_id).first()


def get_user_by_email(session: Session, email: str) -> Optional[User]:
    return session.query(User).filter(User.email == email).first()


def get_user_by_username(session: Session, username: str) -> Optional[User]:
    return session.query(User).filter(User.username == username).first()


def get_users(session: Session, skip: int = 0, limit: int = 100) -> list[Type[User]]:
    return session.query(User).offset(skip).limit(limit).all()


"""
the Asynchronous CRUD classes for get any models from database.
"""


class ReadUsers(BaseCRUD):
    async def execute(self, skip: int = 0, limit: int = 100) -> AsyncIterator[SchemaUser]:
        async with self.async_session.begin() as session:
            async for user in User.get_all(session, skip, limit):
                yield SchemaUser.from_orm(user)


class CreateUser(BaseCRUD):
    async def execute(self, user: Union[SchemaUserCreate, SchemaUserCreateForm]) -> SchemaUser:
        async with self.async_session.begin() as session:

            # Validate by username value. By default, this will validate from database with
            # unique constraint.
            _user = await User.read_by_username(session, user.username)
            if _user:
                raise HTTPException(status_code=409)

            hashed_password = get_password_hash(user.password)
            _user_create: User = User(
                email=user.email,
                username=user.username,
                hashed_password=hashed_password
            )
            session.add(_user_create)

            # `flush`, communicates a series of operations to the database (insert, update, delete).
            # The database maintains them as pending operations in a transaction. The changes aren't
            # persisted permanently to disk, or visible to other transactions until the database
            # receives a COMMIT for the current transaction (which is what session.commit() does).
            # docs: https://stackoverflow.com/questions/4201455/sqlalchemy-whats-the-difference-between-flush-and-commit
            await session.flush()

            # # `commit`, commits (persists) those changes to the database.
            # await session.commit()

            # persisted some changes for an object to the database and need to use this updated
            # object within the same method.
            await session.refresh(_user_create)
            return SchemaUser.from_orm(_user_create)


class ReadUser:
    def __init__(self, session: sessionmaker = Depends(get_async_session)) -> None:
        self.async_session = session

    async def execute(self, user_id: int) -> SchemaUser:
        async with self.async_session.begin() as session:
            user = await User.read_by_id(session, user_id)
            if not user:
                raise HTTPException(status_code=404)
            return SchemaUser.from_orm(user)


class UpdateUser:
    def __init__(self, session: sessionmaker = Depends(get_async_session)) -> None:
        self.async_session = session

    async def execute(self, user_id: int, user: SchemaUserUpdate) -> SchemaUser:
        async with self.async_session.begin() as session:
            _user = await User.read_by_id(session, user_id)
            if not _user:
                raise HTTPException(status_code=404)

            _user.username = user.username
            _user.email = user.email

            await session.flush()
            await session.refresh(_user)
            return SchemaUser.from_orm(_user)


class DeleteUser:
    def __init__(self, session: sessionmaker = Depends(get_async_session)) -> None:
        self.async_session = session

    async def execute(self, user_id: int):
        async with self.async_session.begin() as session:
            user = await User.read_by_id(session, user_id)
            if not user:
                raise HTTPException(status_code=404)

            await session.delete(user)
            await session.flush()
            return SchemaUser.from_orm(user)
