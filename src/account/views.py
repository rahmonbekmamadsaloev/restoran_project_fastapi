from fastapi import Depends, HTTPException, Cookie, Response, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.database import get_session
from .models import UserModel, UserType
from .schemas import (
    CreateUserModelSchema,
    UserModelResponse,
    LoginUserModel,
)
from .helpers import hash_password, verify_password
from jose import JWTError, jwt
from datetime import datetime, timedelta

# Настройки JWT
SECRET_KEY = "super_secret_key"  # вынеси в .env
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

user_admin = APIRouter()


# ===== JWT Утилиты =====
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


# ===== Зависимости =====
async def is_authenticated(session_token: str = Cookie(None), db: AsyncSession = Depends(get_session)):
    if not session_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    payload = decode_token(session_token)
    user_id = int(payload["sub"])

    result = await db.execute(select(UserModel).where(UserModel.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


async def is_admin(current_user: UserModel = Depends(is_authenticated)):
    if current_user.role != UserType.admin:
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return current_user


# ===== Эндпоинты =====
@user_admin.post('/register')
async def register_endpoint(user: CreateUserModelSchema, db: AsyncSession = Depends(get_session)):
    role_value = user.role.lower()
    if role_value not in ["admin", "user"]:
        raise HTTPException(status_code=400, detail="Invalid role")

    # Проверка email
    result = await db.execute(select(UserModel).where(UserModel.email == user.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Проверка username
    result = await db.execute(select(UserModel).where(UserModel.username == user.username))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username already taken")

    # Создание пользователя
    new_user = UserModel(
        username=user.username,
        email=user.email,
        password=hash_password(user.password),
        role=UserType(role_value)
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return {"message": "User registered successfully"}


@user_admin.post('/login')
async def login_endpoint(response: Response, user: LoginUserModel, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(UserModel).where(UserModel.username == user.username))
    login_user = result.scalar_one_or_none()

    if not login_user or not verify_password(user.password, login_user.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # Генерация JWT
    token = create_access_token({"sub": str(login_user.id), "role": login_user.role.value})

    # Сохраняем токен в cookie
    response.set_cookie(key="session_token", value=token, httponly=True)
    return {"message": "Login successful", "token": token}


@user_admin.get('/me')
async def me_endpoint(current_user: UserModel = Depends(is_authenticated)):
    return UserModelResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email
    )


@user_admin.post('/logout')
async def logout_endpoint(response: Response):
    # Просто удаляем cookie (JWT не хранится в БД)
    response.delete_cookie(key="session_token")
    return {"message": "Logged out successfully"}


@user_admin.get('/admin/users')
async def get_all_users(db: AsyncSession = Depends(get_session), current_user: UserModel = Depends(is_admin)):
    result = await db.execute(select(UserModel))
    users = result.scalars().all()
    return [UserModelResponse(id=user.id, username=user.username, email=user.email) for user in users]
