from typing import Optional, List
from sqlalchemy import String, Text, Float, Boolean, DateTime, ForeignKey, Integer, BigInteger
from sqlalchemy.orm import relationship, Mapped, mapped_column
from src.account.models import BaseModel
from src.account.models import UserModel  
from datetime import date, datetime 


class Restoran(BaseModel):
    __tablename__ = "restoran"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    restoran_name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    city: Mapped[str] = mapped_column(String, nullable=True)
    address: Mapped[str] = mapped_column(String, nullable=True)
    rating: Mapped[float] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))

    # связь: каждый ресторан принадлежит одному пользователю
    user = relationship("UserModel", back_populates="restorans")

    dishes: Mapped[list["Dish"]] = relationship("Dish", back_populates="restoran")


class CotigoruDish(BaseModel):
    __tablename__ = "cotigoru_dish"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[Optional[DateTime]] = mapped_column(DateTime)

    dishes: Mapped[List["Dish"]] = relationship("Dish", back_populates="category")


class Dish(BaseModel):
    __tablename__ = "dishes"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    category_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("cotigoru_dish.id"))
    restoran_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("restoran.id"))
    name: Mapped[str] = mapped_column(String, nullable=False)
    price: Mapped[int] = mapped_column(Integer)
    image_url: Mapped[Optional[str]] = mapped_column(Text)
    is_available: Mapped[Optional[bool]] = mapped_column(Boolean, default=True)
    created_at: Mapped[Optional[DateTime]] = mapped_column(DateTime)

    category: Mapped["CotigoruDish"] = relationship("CotigoruDish", back_populates="dishes")
    restoran: Mapped["Restoran"] = relationship("Restoran", back_populates="dishes")
    reviews: Mapped[List["Review"]] = relationship("Review", back_populates="dish")


class Review(BaseModel):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))   # ← исправлено
    dish_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("dishes.id"))
    rating: Mapped[int] = mapped_column(Integer)  # 1–5
    comment: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[Optional[DateTime]] = mapped_column(DateTime)

    user: Mapped["UserModel"] = relationship("UserModel", back_populates="reviews")
    dish: Mapped["Dish"] = relationship("Dish", back_populates="reviews")
