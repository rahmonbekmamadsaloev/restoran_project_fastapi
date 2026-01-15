from sqlalchemy import Column, Integer, String, Enum as SqlEnum, Text,DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase,relationship
import uuid
from enum import Enum
from datetime import datetime

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
    role = Column(SqlEnum(UserType),nullable=False, default=UserType.USER)

    user_session = relationship("SessionModel", back_populates="user")

    def __repr__(self):
        return self.username
    
    
class SessionModel(BaseModel):
    __tablename__ = "sessions_table"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    token = Column(String, unique=True, nullable=False, default=str(uuid.uuid4()))
    created_at = Column(DateTime, default=datetime.now)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)

    user = relationship("UserModel", back_populates="user_session")




