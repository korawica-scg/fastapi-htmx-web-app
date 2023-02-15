from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from . import schemas, crud
from ...database import get_session


tickets = APIRouter(
    prefix="/tickets",
    tags=["tickets"],
    responses={
        404: {"description": "Not found"}
    },
)


@tickets.get("/tickets/", response_model=list[schemas.Item])
def read_items(
        skip: int = 0,
        limit: int = 100,
        session: Session = Depends(get_session)
):
    return crud.get_items(session, skip=skip, limit=limit)
