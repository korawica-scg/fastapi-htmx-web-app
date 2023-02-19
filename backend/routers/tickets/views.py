import uuid
from fastapi import APIRouter
from fastapi import Depends
from fastapi import Cookie
from fastapi import Request
from fastapi import Response
from fastapi.responses import PlainTextResponse
from fastapi import status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from .crud import ReadTicket
from .crud import ReadTickets
from .crud import CreateTicket
from .crud import UpdateTicket
from .crud import DeleteTicket
from .schemas import Ticket as SchemaTicket
from .schemas import TicketCreateForm
from ...dependencies import get_templates

tickets = APIRouter(
    tags=["ticket-views"],
    responses={
        # 404: {"description": "Not found"}
    },
)


@tickets.get("/", response_class=HTMLResponse)
async def ticket_read(
        request: Request,
        session_key: str = Cookie(default=uuid.uuid4().hex),
        template: Jinja2Templates = Depends(get_templates),
        service: ReadTickets = Depends(ReadTickets),
):
    _tickets = service.execute(session_key)
    context = {
        "request": request,
        "tickets": [ticket async for ticket in _tickets],
        "title": "Home"
    }
    response = template.TemplateResponse("tickets/index.html", context)
    response.set_cookie(
        key="session_key",
        value=session_key,
        expires=(60 * 60 * 24 * 3)
    )
    return response


@tickets.post("/", response_class=HTMLResponse)
async def ticket_create(
        request: Request,
        ticket: TicketCreateForm = Depends(TicketCreateForm.as_form),
        template: Jinja2Templates = Depends(get_templates),
        service: CreateTicket = Depends(CreateTicket),
):
    session_key = request.cookies.get("session_key")
    ticket: SchemaTicket = await service.execute(ticket=ticket, session_key=session_key)
    context = {"request": request, "ticket": ticket}
    return template.TemplateResponse("tickets/partials/ticket.html", context)


@tickets.get("/{item_id}/", response_class=HTMLResponse)
async def ticket_update_get(
        request: Request,
        item_id: int,
        template: Jinja2Templates = Depends(get_templates),
        service: ReadTicket = Depends(ReadTicket),
):
    ticket = await service.execute(item_id)
    context = {"request": request, "ticket": ticket}
    return template.TemplateResponse("tickets/partials/ticket_edit.html", context)


@tickets.put("/{item_id}/", response_class=HTMLResponse)
async def ticket_update_put(
        request: Request,
        item_id: int,
        ticket: TicketCreateForm = Depends(TicketCreateForm.as_form),
        template: Jinja2Templates = Depends(get_templates),
        service: UpdateTicket = Depends(UpdateTicket),
):
    ticket = await service.execute(item_id, ticket)
    context = {"request": request, "ticket": ticket}
    return template.TemplateResponse("tickets/partials/ticket.html", context)


@tickets.delete("/{item_id}/", response_class=PlainTextResponse)
async def ticket_delete(
        item_id: int,
        service: DeleteTicket = Depends(DeleteTicket),
):
    await service.execute(item_id)
    return ""
