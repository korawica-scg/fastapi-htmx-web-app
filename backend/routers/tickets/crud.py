from fastapi import Depends
from fastapi import HTTPException
from typing import AsyncIterator
from sqlalchemy.orm import Session
from .models import Ticket
from .models import UserTicket
from .schemas import Ticket as SchemaTicket
from .schemas import TicketCreate as SchemaTicketCreate
from .schemas import TicketCreateForm
from ...database import BaseCRUD
from ...database import get_async_session


def get_tickets(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Ticket).offset(skip).limit(limit).all()


def create_user_ticket(session: Session, item: SchemaTicketCreate, user_id: int):
    item = Ticket(
        **item.dict(),
        owner_id=user_id
    )
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


class CreateTicket(BaseCRUD):
    async def execute(self, ticket: TicketCreateForm, session_key: str) -> SchemaTicket:
        async with self.async_session.begin() as session:
            ticket_create = Ticket(
                text=ticket.text,
                description=ticket.description,
                session_key=session_key
            )
            session.add(ticket_create)
            await session.flush()
            await session.refresh(ticket_create)
            return SchemaTicket.from_orm(ticket_create)


class ReadTicket(BaseCRUD):
    async def execute(self, ticket_id: int) -> SchemaTicket:
        async with self.async_session.begin() as session:
            ticket = await Ticket.read_by_id(session, ticket_id)
            if not ticket:
                raise HTTPException(status_code=404)
            return SchemaTicket.from_orm(ticket)


class ReadTickets(BaseCRUD):
    async def execute(self, session_key) -> AsyncIterator[SchemaTicket]:
        async with self.async_session.begin() as session:
            async for ticket in Ticket.read_all(session, session_key):
                yield SchemaTicket.from_orm(ticket)


class UpdateTicket(BaseCRUD):
    async def execute(self, ticket_id: int, ticket: TicketCreateForm) -> SchemaTicket:
        async with self.async_session.begin() as session:
            _ticket = await Ticket.read_by_id(session, ticket_id)
            if not _ticket:
                raise HTTPException(status_code=404)

            _ticket.text = ticket.text
            _ticket.description = ticket.description

            await session.flush()
            await session.refresh(_ticket)
            return SchemaTicket.from_orm(_ticket)


class DeleteTicket(BaseCRUD):
    async def execute(self, ticket_id: int):
        async with self.async_session.begin() as session:
            ticket = await Ticket.read_by_id(session, ticket_id)
            print(ticket)
            # if not ticket:
            #     raise HTTPException(status_code=404)

            await session.delete(ticket)
            await session.flush()
            return SchemaTicket.from_orm(ticket)


class CreateUserTicket:
    def __init__(self, session: Session = Depends(get_async_session)) -> None:
        self.async_session = session

    async def execute(self, ticket: SchemaTicketCreate, user_id: int) -> SchemaTicket:
        async with self.async_session.begin() as session:
            ticket = UserTicket(
                text=ticket.text,
                description=ticket.description,
                owner_id=user_id
            )
            session.add(ticket)
            await session.flush()
            await session.refresh(ticket)
            return SchemaTicket.from_orm(ticket)


class ReadUserTickets:
    ...


class UpdateUserTicket:
    ...


class DeleteUserTicket:
    ...
