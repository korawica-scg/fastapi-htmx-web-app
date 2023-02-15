from typing import Union
from pydantic import (
    BaseModel,
)


class ItemBase(BaseModel):
    text: str
    description: Union[str, None] = None


class ItemCreate(ItemBase):
    pass


class Item(ItemBase):
    id: int
    owner_id: int
    completed: bool

    class Config:
        orm_mode = True
