from fastapi import (
    Depends,
    HTTPException,
    APIRouter,
)
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from datetime import datetime, timedelta
from jose import JWTError, jwt

from src.database import get_session
from .models import UserModel, UserType, UserProfile
from .schemas import (
    CreateUserModelSchema,
    UserModelResponse,
    LoginUserModel,
    UpdateUserProfileSchema,
)
from .helpers import hash_password, verify_password


# ================== JWT SETTINGS ==================

SECRET_KEY = "super_secret_key"  # вынеси в .env
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

security = HTTPBearer()

user_admin = APIRouter()


# ================== JWT UTILS ==================

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ================== DEPENDENCIES ==================

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_session),
) -> UserModel:
    token = credentials.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
    except (JWTError, TypeError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid token")

    result = await db.execute(select(UserModel).where(UserModel.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


async def is_admin(current_user: UserModel = Depends(get_current_user)):
    if current_user.role != UserType.admin:
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return current_user


# ================== REGISTER ==================

@user_admin.post("/register", tags=['auth'])
async def register_endpoint(
    user: CreateUserModelSchema,
    db: AsyncSession = Depends(get_session),
):
    role_value = user.role.lower()
    if role_value not in ("admin", "user"):
        raise HTTPException(status_code=400, detail="Invalid role")

    if await db.scalar(select(UserModel).where(UserModel.email == user.email)):
        raise HTTPException(status_code=400, detail="Email already registered")

    if await db.scalar(select(UserModel).where(UserModel.username == user.username)):
        raise HTTPException(status_code=400, detail="Username already taken")

    new_user = UserModel(
        username=user.username,
        email=user.email,
        password=hash_password(user.password),
        role=UserType(role_value),
    )
    db.add(new_user)
    await db.flush()

    db.add(UserProfile(user_id=new_user.id))
    await db.commit()

    return {"message": "User registered successfully"}


# ================== LOGIN ==================

@user_admin.post("/login", tags=['auth'])
async def login_endpoint(
    user: LoginUserModel,
    db: AsyncSession = Depends(get_session),
):
    result = await db.execute(
        select(UserModel).where(UserModel.username == user.username)
    )
    login_user = result.scalar_one_or_none()

    if not login_user or not verify_password(user.password, login_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(
        {"sub": str(login_user.id), "role": login_user.role.value}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


# ================== LOGOUT ==================

@user_admin.post("/logout", tags=['auth'])
async def logout_endpoint(
    current_user: UserModel = Depends(get_current_user),
):
    return {"message": "Logged out successfully"}


# ================== ME ==================

@user_admin.get("/me", response_model=UserModelResponse)
async def me_endpoint(
    current_user: UserModel = Depends(get_current_user),
):
    return current_user


# ================== ADMIN ==================

@user_admin.get("/admin/users")
async def get_all_users(
    db: AsyncSession = Depends(get_session),
    _: UserModel = Depends(is_admin),
):
    result = await db.execute(select(UserModel))
    users = result.scalars().all()
    return users


# ================== PROFILE ==================

@user_admin.get("/me-profile")
async def get_my_profile(
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    return profile


@user_admin.put("/me-profile")
async def update_my_profile(
    profile_data: UpdateUserProfileSchema,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    for field, value in profile_data.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)

    await db.commit()
    await db.refresh(profile)

    return {
        "message": "Profile updated successfully",
        "profile": profile,
    }

