from ...database import Base
from sqlalchemy.orm import relationship
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    firstname = Column(String)
    lastname = Column(String)
    hashed_password = Column(String)
    role = Column(String, nullable=True, default='user')
    is_active = Column(Boolean, default=True)

    # Create relationship to TODOs
    todos = relationship("TODO", back_populates="owner", cascade="all, delete-orphan")



