from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.database import get_session
from .model import Restoran, CotigoruDish, Dish, Review
from .schemas import (
    RestoranCreate, RestoranResponse,
    CategoryCreate, CategoryResponse,
    DishCreate, DishResponse,
    ReviewCreate, ReviewResponse
)
from src.account.views import get_current_user
from src.account.models import UserModel

router = APIRouter()


# ================== RESTORAN ==================

@router.post("/restorans", response_model=RestoranResponse)
async def create_restoran(
    restoran: RestoranCreate,
    db: AsyncSession = Depends(get_session),
    current_user: UserModel = Depends(get_current_user)
):
    new_restoran = Restoran(
        **restoran.dict(),
        user_id=current_user.id
    )
    db.add(new_restoran)
    await db.commit()
    await db.refresh(new_restoran)
    return new_restoran


@router.get("/restorans", response_model=list[RestoranResponse])
async def get_restorans(db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Restoran))
    return result.scalars().all()


# ================== CATEGORY ==================

@router.post("/categories", response_model=CategoryResponse)
async def create_category(
    category: CategoryCreate,
    db: AsyncSession = Depends(get_session),
    current_user: UserModel = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only authenticated users can add categories"
        )

    new_category = CotigoruDish(**category.dict())
    db.add(new_category)
    await db.commit()
    await db.refresh(new_category)
    return new_category


@router.get("/categories", response_model=list[CategoryResponse])
async def get_categories(db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(CotigoruDish))
    return result.scalars().all()


# ================== DISH ==================

@router.post("/dishes", response_model=DishResponse)
async def create_dish(
    dish: DishCreate,
    db: AsyncSession = Depends(get_session),
    current_user: UserModel = Depends(get_current_user)
):
    new_dish = Dish(**dish.dict())
    db.add(new_dish)
    await db.commit()
    await db.refresh(new_dish)
    return new_dish


@router.get("/dishes", response_model=list[DishResponse])
async def get_dishes(
    name: str | None = Query(default=None, description="Фильтр по названию блюда"),
    db: AsyncSession = Depends(get_session)
):
    query = select(Dish)
    if name:
        query = query.where(Dish.name.ilike(f"%{name}%"))
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/dishes/{dish_id}", response_model=DishResponse)
async def get_dish(dish_id: int, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Dish).where(Dish.id == dish_id))
    dish = result.scalar_one_or_none()
    if not dish:
        raise HTTPException(status_code=404, detail="Dish not found")
    return dish


# ================== REVIEW ==================

@router.post("/reviews", response_model=ReviewResponse)
async def create_review(
    review: ReviewCreate,
    db: AsyncSession = Depends(get_session),
    current_user: UserModel = Depends(get_current_user)
):
    new_review = Review(
        **review.dict(),
        user_id=current_user.id
    )
    db.add(new_review)
    await db.commit()
    await db.refresh(new_review)
    return new_review


@router.get("/reviews", response_model=list[ReviewResponse])
async def get_reviews(db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Review))
    return result.scalars().all()


@router.get("/reviews/{review_id}", response_model=ReviewResponse)
async def get_review(review_id: int, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Review).where(Review.id == review_id))
    review = result.scalar_one_or_none()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review
