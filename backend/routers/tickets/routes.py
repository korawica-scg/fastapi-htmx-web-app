from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session
from .schemas import Ticket as SchemaTicket
from .schemas import TicketCreate as SchemaTicketCreate
from .crud import get_tickets
from .crud import CreateTicket
from ...database import get_session


tickets = APIRouter(
    prefix="/tickets",
    tags=["tickets"],
    responses={
        404: {"description": "Not found"}
    },
)


@tickets.get("/", response_model=list[SchemaTicket])
def read_all(
        skip: int = 0,
        limit: int = 100,
        session: Session = Depends(get_session)
):
    return get_tickets(session, skip=skip, limit=limit)


@tickets.post("/", response_model=SchemaTicket)
async def create(
    user: SchemaTicketCreate,
    service: CreateTicket = Depends(CreateTicket),
) -> SchemaTicket:
    """CRUD of user"""
    return await service.execute(user)
