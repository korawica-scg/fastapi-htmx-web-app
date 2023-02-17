from fastapi import APIRouter
from fastapi import Depends
from fastapi import Path
from fastapi import Form
from fastapi import status
from .dependencies import get_token_header
from .schemas import User as SchemaUser
from .schemas import UserCreate as SchemaUserCreate
from .schemas import UserUpdate as SchemaUserUpdate
from .crud import ReadUsers
from .crud import ReadUser
from .crud import CreateUser
from .crud import UpdateUser
from .crud import DeleteUser
from ..tickets.schemas import Ticket as SchemaTicket
from ..tickets.schemas import TicketCreate as SchemaTicketCreate
from ..tickets.crud import CreateUserTicket


users = APIRouter(
    prefix="/users",
    tags=["users"],
    # dependencies=[Depends(get_token_header)],
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Not found"},
    },
)


@users.get("/", response_model=list[SchemaUser])
async def read_all(
    skip: int = 0,
    limit: int = 100,
    service: ReadUsers = Depends(ReadUsers),
):
    """CRUD of user"""
    return [user async for user in service.execute(skip=skip, limit=limit)]


@users.post("/", response_model=SchemaUser)
async def create(
    user: SchemaUserCreate,
    service: CreateUser = Depends(CreateUser),
) -> SchemaUser:
    """CRUD of user"""
    user: SchemaUser = await service.execute(user)
    return user


@users.put("/{user_id}", response_model=SchemaUser)
async def update(
    user: SchemaUserUpdate,
    user_id: int = Path(title="The ID of the user to get", ge=1),
    service: UpdateUser = Depends(UpdateUser),
) -> SchemaUser:
    """CRUD of user"""
    return await service.execute(user_id, user)


@users.delete("/{user_id}", response_model=SchemaUser)
async def delete(
    user_id: int = Path(title="The ID of the user to get", ge=1),
    service: DeleteUser = Depends(DeleteUser),
) -> SchemaUser:
    """CRUD of user"""
    return await service.execute(user_id)


@users.get("/{user_id}", response_model=SchemaUser)
async def read(
    user_id: int = Path(title="The ID of the user to get", ge=1),
    service: ReadUser = Depends(ReadUser),
):
    """CRUD of user"""
    return await service.execute(user_id)


@users.post("/{user_id}/tickets/", response_model=SchemaTicket)
async def create_ticket(
    ticket: SchemaTicketCreate,
    user_id: int = Path(title="The ID of the user to get", ge=1),
    service: CreateUserTicket = Depends(CreateUserTicket),
) -> SchemaTicket:
    """CRUD of user's ticket"""
    return await service.execute(ticket, user_id)
