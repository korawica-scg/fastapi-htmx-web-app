from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from . import schemas
from .models import User
from ...database import get_async_session


def get_user(session: Session, user_id: int):
    return session.query(User).filter(User.id == user_id).first()


def get_user_by_email(session: Session, email: str):
    return session.query(User).filter(User.email == email).first()


def get_user_by_username(session: Session, username: str):
    return session.query(User).filter(User.username == username).first()


def get_users(session: Session, skip: int = 0, limit: int = 100):
    return session.query(User).offset(skip).limit(limit).all()


def create_user(session: Session, user: schemas.UserCreate):
    fake_hashed_password = f'{user.password}****'
    user = User(
        email=user.email,
        username=user.username,
        firstname=user.firstname,
        lastname=user.lastname,
        hashed_password=fake_hashed_password
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


class CreateUser:
    def __init__(self, session: Session = Depends(get_async_session)) -> None:
        self.async_session = session

    async def execute(self, user: schemas.UserCreate) -> schemas.User:
        async with self.async_session.begin() as session:
            fake_hashed_password = f'{user.password}****'
            user = User(
                email=user.email,
                username=user.username,
                firstname=user.firstname,
                lastname=user.lastname,
                hashed_password=fake_hashed_password
            )
            session.add(user)
            await session.flush()
            return schemas.User.from_orm(user)
