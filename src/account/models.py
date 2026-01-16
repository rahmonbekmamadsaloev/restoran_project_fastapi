from sqlalchemy import (
    Column,
    Integer,
    String,
    Enum as SqlEnum,
    DateTime,
    ForeignKey,
    Date
)
from sqlalchemy.orm import DeclarativeBase, relationship
from enum import Enum
from datetime import datetime, date
import uuid


class BaseModel(DeclarativeBase):
    pass


class UserType(Enum):
    ADMIN = "admin"
    USER = "user"


class UserModel(BaseModel):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(SqlEnum(UserType), nullable=False, default=UserType.USER)
    created_at = Column(Date, default=date.today)

    # связи
    profile = relationship(
        "UserProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    user_session = relationship(
        "SessionModel",
        back_populates="user",
        cascade="all, delete"
    )

    def __repr__(self):
        return self.username


class UserProfile(BaseModel):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )

    username = Column(String(100))
    email = Column(String(100))
    number = Column(Integer, nullable=True)
    image_profile = Column(String, nullable=True)

    user = relationship("UserModel", back_populates="profile")


class SessionModel(BaseModel):
    __tablename__ = "sessions_table"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    token = Column(String, unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=datetime.utcnow)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    user = relationship("UserModel", back_populates="user_session")
