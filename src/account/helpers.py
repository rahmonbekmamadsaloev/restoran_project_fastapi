from passlib.hash import pbkdf2_sha256
from sqlalchemy import select
from src.database import SessionLocal
from .models import UserModel

def hash_password(password: str) -> str:
    """Хэшируем пароль"""
    return pbkdf2_sha256.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Проверяем пароль"""
    return pbkdf2_sha256.verify(password, password_hash)


async def authenticate(username: str, password: str, db):
    """Аутентификация пользователя (асинхронная)"""
    # выполняем асинхронный запрос
    result = await db.execute(
        select(UserModel).where(UserModel.username == username)
    )
    user = result.scalar_one_or_none()

    if user and verify_password(password, user.password):
        return user
    return None





