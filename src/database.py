from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

# URL подключения к базе (SQLite для примера)
DATABASE_URL = "sqlite+aiosqlite:///./restoran.db"

# Создаём движок
engine = create_async_engine(DATABASE_URL, echo=True)

# Фабрика асинхронных сессий
SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

# Базовый класс для моделей
Base = declarative_base()

# Dependency для FastAPI
async def get_session():
    async with SessionLocal() as session:
        yield session
