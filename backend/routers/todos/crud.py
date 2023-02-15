from sqlalchemy.orm import Session
from .schemas import ItemCreate
from .models import TODO


def get_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(TODO).offset(skip).limit(limit).all()


def create_user_item(session: Session, item: ItemCreate, user_id: int):
    item = TODO(
        **item.dict(),
        owner_id=user_id
    )
    session.add(item)
    session.commit()
    session.refresh(item)
    return item
