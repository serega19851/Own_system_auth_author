from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

# Импортируем настройки из централизованной конфигурации
from app.config import config


engine = create_async_engine(
    config.db.DATABASE_URL,
    echo=True,  # Включает логирование SQL запросов
    future=True
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

class Base(DeclarativeBase):
    pass
# Base = declarative_base()


# Функция для получения сессии базы данных
async def get_db():
    """Получение сессии базы данных"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
