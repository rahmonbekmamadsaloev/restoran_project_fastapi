from pydantic import BaseModel
from typing import Optional, List


# ================== RESTORAN ==================

class RestoranBase(BaseModel):
    restoran_name: str
    description: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    rating: Optional[float] = None


class RestoranCreate(RestoranBase):
    pass


class RestoranResponse(RestoranBase):
    id: int
    user_id: int
    created_at: Optional[str] = None

    class Config:
        from_attributes = True




# ================== CATEGORY (CotigoruDish) ==================

class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryResponse(CategoryBase):
    id: int
    created_at: Optional[int] = None

    class Config:
        orm_mode = True


# ================== DISH ==================

class DishBase(BaseModel):
    name: str
    price: int
    image_url: Optional[str] = None
    is_available: Optional[bool] = True


class DishCreate(DishBase):
    category_id: int
    restron_id: int


class DishResponse(DishBase):
    id: int
    category_id: int
    restron_id: int
    created_at: Optional[int] = None

    class Config:
        orm_mode = True


# ================== REVIEW ==================

class ReviewBase(BaseModel):
    rating: int
    comment: Optional[str] = None


class ReviewCreate(ReviewBase):
    user_id: int
    dish_id: int


class ReviewResponse(ReviewBase):
    id: int
    user_id: int
    dish_id: int
    created_at: Optional[int] = None

    class Config:
        orm_mode = True
