from fastapi import (
    Request,
    APIRouter,
    Depends,
    HTTPException,
    Path,
    Form,
    status,
)
from sqlalchemy.orm import Session
from .dependencies import get_token_header
from .schemas import User as SchemaUser
from .schemas import UserCreate as SchemaUserCreate
from .schemas import UserUpdate as SchemaUserUpdate
from .schemas import Item
from .crud import ReadUsers
from .crud import ReadUser
from .crud import CreateUser
from .crud import UpdateUser
from .crud import DeleteUser
from .crud import get_user
from ..tickets.schemas import ItemCreate
from ..tickets.crud import create_user_item
from ...database import get_session


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
    return await service.execute(user)


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


@users.post("/{user_id}/todos/", response_model=Item)
def create_item_for_user(
        item: ItemCreate,
        user_id: int = Path(title="The ID of the user to get", ge=1),
        session: Session = Depends(get_session),
):
    return create_user_item(session=session, item=item, user_id=user_id)
