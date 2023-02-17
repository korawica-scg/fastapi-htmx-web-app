from typing import AsyncIterator
from typing import Optional
from sqlalchemy.orm import relationship, selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    select
)
from ...database import Base


class User(Base):
    """User model"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

    # Create role inline for user.
    # role = Column(String, nullable=True, default='user')

    # Create relationship to Tickets model
    tickets = relationship(
        "UserTicket",
        back_populates="owner",
        order_by="UserTicket.id",
        cascade="save-update, merge, refresh-expire, expunge, delete, delete-orphan",
    )

    @classmethod
    async def read_by_username(
            cls,
            session: AsyncSession,
            username: str,
            include_tickets: bool = False,
    ) -> Optional['User']:
        """Return User that filter by username"""
        stmt = select(cls).where(cls.username == username)
        if include_tickets:
            stmt = stmt.options(selectinload(cls.tickets))
        result = (await session.execute(stmt.order_by(cls.id))).first()
        return result.User if result else None

    @classmethod
    async def read_by_id(
            cls, session: AsyncSession,
            user_id: int,
            include_tickets: bool = False
    ) -> Optional['User']:
        stmt = select(cls).where(cls.id == user_id)
        if include_tickets:
            stmt = stmt.options(selectinload(cls.tickets))
        result = (await session.execute(stmt.order_by(cls.id))).first()
        return result.User if result else None

    @classmethod
    async def get_all(
            cls,
            session: AsyncSession,
            skip: int = 0,
            limit: int = 100,
            include_tickets: bool = False,
    ) -> AsyncIterator['User']:
        stmt = select(cls)
        if include_tickets:
            stmt = stmt.options(selectinload(cls.tickets))
        if skip > 0 and limit > 0:
            stmt = stmt.offset(skip).limit(limit)
        stream = await session.stream(stmt.order_by(cls.id))
        async for row in stream:
            yield row.User
