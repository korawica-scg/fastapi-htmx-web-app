from pydantic import (
    BaseModel,
    EmailStr,
)
from ..todos.schemas import Item


class UserBase(BaseModel):
    email: EmailStr
    username: str


class UserCreate(UserBase):
    lastname: str
    firstname: str
    password: str


class User(UserBase):
    id: int
    is_active: bool
    items: list[Item] = []

    class Config:
        orm_mode = True
