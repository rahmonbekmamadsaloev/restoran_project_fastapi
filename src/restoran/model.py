from typing import Optional, List
from sqlalchemy import String, Text, Float, Boolean, DateTime, ForeignKey, Integer, BigInteger
from sqlalchemy.orm import relationship, Mapped, mapped_column
from src.database import Base
from src.account.models import UserModel   

class Restoran(Base):
    __tablename__ = "restoran"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    restoran_name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    city: Mapped[Optional[str]] = mapped_column(String)
    address: Mapped[Optional[str]] = mapped_column(String)
    rating: Mapped[Optional[float]] = mapped_column(Float)
    created_at: Mapped[Optional[DateTime]] = mapped_column(DateTime)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))  # ← исправлено

    owner: Mapped["UserModel"] = relationship("UserModel", back_populates="restorans")
    dishes: Mapped[List["Dish"]] = relationship("Dish", back_populates="restoran")


class CotigoruDish(Base):
    __tablename__ = "cotigoru_dish"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[Optional[DateTime]] = mapped_column(DateTime)

    dishes: Mapped[List["Dish"]] = relationship("Dish", back_populates="category")


class Dish(Base):
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


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))   # ← исправлено
    dish_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("dishes.id"))
    rating: Mapped[int] = mapped_column(Integer)  # 1–5
    comment: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[Optional[DateTime]] = mapped_column(DateTime)

    user: Mapped["UserModel"] = relationship("UserModel", back_populates="reviews")
    dish: Mapped["Dish"] = relationship("Dish", back_populates="reviews")
