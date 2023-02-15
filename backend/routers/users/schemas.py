from pydantic import EmailStr
from pydantic import BaseModel
from pydantic import Field
from ..tickets.schemas import Item


class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=1, max_length=100)


class UserCreate(UserBase):
    password: str


class UserUpdate(UserBase):
    ...


class User(UserBase):
    id: int
    is_active: bool
    todos: list[Item] = Field(min_items=0)

    class Config:
        orm_mode = True
