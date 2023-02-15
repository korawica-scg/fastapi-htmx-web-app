from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from . import schemas, crud
from ...database import get_session


items = APIRouter(
    prefix="/items",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


@items.get("/items/", response_model=list[schemas.Item])
def read_items(skip: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    return crud.get_items(session, skip=skip, limit=limit)
