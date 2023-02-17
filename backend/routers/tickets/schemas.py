from fastapi import Form
from typing import Union
from pydantic import BaseModel


class TicketBase(BaseModel):
    text: str
    description: Union[str, None] = None


class TicketCreate(TicketBase):
    session_key: str


class Ticket(TicketBase):
    id: int
    session_key: str

    class Config:
        orm_mode = True


class TicketCreateForm(TicketBase):

    @classmethod
    def as_form(
            cls,
            text: str = Form(...),
            description: Union[str, None] = Form(None)
    ):
        return cls(text=text, description=description)


class UserTicketCreate(TicketBase):
    owner_id: int


class UserTicket(TicketBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True
