from pydantic import EmailStr
from pydantic import BaseModel
from pydantic import Field
from fastapi import Form
from typing import Optional, Union
from ..tickets.schemas import Ticket


class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=1, max_length=100)


class UserCreate(UserBase):
    password: str


class UserUpdate(UserBase):
    ...


class UserCreateForm(UserBase):
    password: str

    @classmethod
    def as_form(
            cls,
            email: EmailStr = Form(...),
            username: str = Form(...),
            password: str = Form(...)
    ):
        return cls(email=email, username=username, password=password)


class User(UserBase):
    id: int
    is_active: bool
    is_superuser: bool

    # FIXME: sqlalchemy.exc.MissingGreenlet
    # tickets: list[Ticket] = Field(min_items=0)

    class Config:
        orm_mode = True
