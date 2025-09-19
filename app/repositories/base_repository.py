from typing import TypeVar, Type, Optional, List, Dict, Any, Generic
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from sqlalchemy.exc import SQLAlchemyError

T = TypeVar('T')

class BaseRepository(Generic[T]):
    """
    Базовый репозиторий для работы с моделями SQLAlchemy
    Предоставляет стандартные CRUD операции
    """
    
    def __init__(self, db: AsyncSession, model_class: Type[T]):
        self.db = db
        self.model_class = model_class
    
    async def get_by_id(self, id: int) -> Optional[T]:
        """Получить объект по ID"""
        try:
            result = await self.db.execute(
                select(self.model_class).where(self.model_class.id == id)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            
            raise e
    
    async def get_all(self, **filters) -> List[T]:
        """
        Получить все объекты с фильтрацией
        
        Args:
            **filters: Фильтры в виде field_name=value
        
        Returns:
            List[T]: Список объектов
        """
        try:
            query = select(self.model_class)
            
            # Применяем фильтры
            for field_name, value in filters.items():
                if hasattr(self.model_class, field_name):
                    field = getattr(self.model_class, field_name)
                    query = query.where(field == value)
            
            result = await self.db.execute(query)
            return result.scalars().all()
        except SQLAlchemyError as e:
            raise e
    
    async def create(self, entity: T) -> T:
        """Создать новый объект"""
        try:
            self.db.add(entity)
            await self.db.flush()  # Flush вместо commit для получения ID
            await self.db.refresh(entity)
            return entity
        except SQLAlchemyError as e:
            raise e
    
    async def update(self, entity: T) -> T:
        """Обновить существующий объект"""
        try:
            await self.db.flush()  # Flush вместо commit
            await self.db.refresh(entity)
            return entity
        except SQLAlchemyError as e:
            raise e
    
    async def delete(self, id: int) -> bool:
        """
        Удалить объект по ID
        
        Args:
            id: ID объекта для удаления
            
        Returns:
            bool: True если объект был удален, False если не найден
        """
        try:
            result = await self.db.execute(
                delete(self.model_class).where(self.model_class.id == id)
            )
            await self.db.flush()  # Flush вместо commit
            return result.rowcount > 0
        except SQLAlchemyError as e:
            raise e
    
    async def count(self, **filters) -> int:
        """
        Подсчитать количество объектов с фильтрацией
        
        Args:
            **filters: Фильтры в виде field_name=value
            
        Returns:
            int: Количество объектов
        """
        try:
            query = select(func.count(self.model_class.id))
            
            # Применяем фильтры
            for field_name, value in filters.items():
                if hasattr(self.model_class, field_name):
                    field = getattr(self.model_class, field_name)
                    query = query.where(field == value)
            
            result = await self.db.execute(query)
            return result.scalar()
        except SQLAlchemyError as e:
            
            raise e
    
    async def exists(self, id: int) -> bool:
        """Проверить существование объекта по ID"""
        try:
            result = await self.db.execute(
                select(func.count(self.model_class.id)).where(self.model_class.id == id)
            )
            return result.scalar() > 0
        except SQLAlchemyError as e:
            
            raise e
    
    async def get_with_limit(self, limit: int = 100, offset: int = 0, **filters) -> List[T]:
        """Получить объекты с пагинацией"""
        try:
            query = select(self.model_class)
            
            # Применяем фильтры
            for field_name, value in filters.items():
                if hasattr(self.model_class, field_name):
                    field = getattr(self.model_class, field_name)
                    query = query.where(field == value)
            
            query = query.limit(limit).offset(offset)
            result = await self.db.execute(query)
            return result.scalars().all()
        except SQLAlchemyError as e:
            
            raise e
