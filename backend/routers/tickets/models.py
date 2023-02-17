from typing import AsyncIterator
from typing import Optional
from sqlalchemy.orm import relationship, joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    select
)
from ...database import Base


class Ticket(Base):
    """Ticket model"""
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, index=True)
    description = Column(String, index=True)
    session_key = Column(String, index=True)
    create_at = Column(DateTime, default=datetime.now)
    update_at = Column(DateTime, default=datetime.now)

    @classmethod
    async def read_all(cls, session: AsyncSession, session_key: str) -> AsyncIterator['Ticket']:
        stmt = (
            select(cls).where(cls.session_key == session_key)
        )
        stream = await session.stream(stmt.order_by(cls.id))
        async for row in stream:
            yield row.Ticket

    @classmethod
    async def read_by_id(cls, session: AsyncSession, ticket_id: int) -> Optional['Ticket']:
        stmt = select(cls).where(cls.id == ticket_id)
        result = (await session.execute(stmt.order_by(cls.id))).first()
        return result.Ticket if result else None


class UserTicket(Base):
    """User's ticket model"""
    __tablename__ = "user_tickets"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, index=True)
    description = Column(String, index=True)
    create_at = Column(DateTime, default=datetime.now)

    # Create ForeignKey for reference primary of User model
    owner_id = Column(Integer, ForeignKey("users.id"))

    # Create relationship to User
    owner = relationship("User", back_populates="tickets")

    @classmethod
    async def read_all(cls, session: AsyncSession, user_id: int) -> AsyncIterator['UserTicket']:
        stmt = (
            select(cls)
                .where(cls.owner_id == user_id)
                .options(joinedload(cls.owner, innerjoin=True))
        )
        stream = await session.stream(stmt.order_by(cls.id))
        async for row in stream:
            yield row.Ticket

    @classmethod
    async def read_by_id(cls, session: AsyncSession, ticket_id: int) -> Optional['UserTicket']:
        stmt = select(cls).where(cls.id == ticket_id).options(joinedload(cls.owner))
        result = (await session.execute(stmt.order_by(cls.id))).first()
        return result.UserTicket if result else None

    @classmethod
    async def read_by_ids(cls, session: AsyncSession, ticket_ids: list[int]) -> AsyncIterator['UserTicket']:
        stmt = (
            select(cls)
                .where(cls.id.in_(ticket_ids))
                .options(joinedload(cls.owner))
        )
        stream = await session.stream(stmt.order_by(cls.id))
        async for row in stream:
            yield row.UserTicket

    @classmethod
    async def create(
            cls, session: AsyncSession, owner_id: int, text: str, description: str
    ) -> 'UserTicket':
        ticket: 'Ticket' = UserTicket(text=text, description=description, owner_id=owner_id)
        session.add(ticket)
        await session.flush()
        await session.refresh(ticket)
        return ticket

    @classmethod
    async def delete(cls, session: AsyncSession, ticket: 'UserTicket') -> None:
        await session.delete(ticket)
        await session.flush()
