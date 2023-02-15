from ...database import Base
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    JSON,
)


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, index=True)
    description = Column(String, index=True)
    data = Column(JSON)
    completed = Column(Boolean, default=False)
    create_at = Column(DateTime, default=datetime.now)

    # Create ForeignKey for reference primary of User model
    owner_id = Column(Integer, ForeignKey("users.id"))

    # Create relationship to User
    owner = relationship("User", back_populates="tickets")
