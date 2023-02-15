from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Form,
    status,
)
from sqlalchemy.orm import Session
from .dependencies import get_token_header
from . import (
    schemas,
    crud,
)
from ..todos.schemas import ItemCreate
from ..todos.crud import create_user_item
from ...database import get_session


users = APIRouter(
    prefix="/users",
    tags=["users"],
    # dependencies=[Depends(get_token_header)],
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Not found"}
    },
)


@users.post("/", response_model=schemas.User)
def create_user(
        user: schemas.UserCreate,
        session: Session = Depends(get_session),
):
    db_user = crud.get_user_by_email(session, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(session=session, user=user)


@users.get("/", response_model=list[schemas.User])
def read_users(
        skip: int = 0,
        limit: int = 100,
        session: Session = Depends(get_session),
):
    return crud.get_users(session, skip=skip, limit=limit)


@users.get("/{user_id}", response_model=schemas.User)
def read_user(
        user_id: int,
        session: Session = Depends(get_session),
):
    db_user = crud.get_user(session, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@users.post("/{user_id}/items/", response_model=schemas.Item)
def create_item_for_user(
        user_id: int,
        item: ItemCreate,
        session: Session = Depends(get_session),
):
    return create_user_item(session=session, item=item, user_id=user_id)


@users.post(
    "/new",
    response_model=schemas.User
)
async def create(
    user: schemas.UserCreate,
    service: crud.CreateUser = Depends(crud.CreateUser),
) -> schemas.User:
    return await service.execute(user)
