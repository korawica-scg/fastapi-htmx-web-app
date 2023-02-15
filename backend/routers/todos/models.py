from ...database import Base
from sqlalchemy.orm import relationship
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
)


class TODO(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, index=True)
    description = Column(String, index=True)
    completed = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"))

    # Create relationship to User
    owner = relationship("User", back_populates="todos")
