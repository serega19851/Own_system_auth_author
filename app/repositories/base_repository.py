from typing import TypeVar, Type, Optional, List, Dict, Any, Generic, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from ..exceptions.database_exceptions import DatabaseException, IntegrityException
from ..utils.logger import get_logger

T = TypeVar('T')

class BaseRepository(Generic[T]):
    """
    Базовый репозиторий для работы с моделями SQLAlchemy
    Предоставляет стандартные CRUD операции с единообразной обработкой исключений
    """
    
    def __init__(self, db: AsyncSession, model_class: Type[T]):
        self.db = db
        self.model_class = model_class
        self.logger = get_logger(self.__class__.__name__)
    
    async def get_by_id(self, id: int) -> Optional[T]:
        """Получить объект по ID"""
        try:
            result = await self.db.execute(
                select(self.model_class).where(self.model_class.id == id)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            self.logger.error(f"Database error in get_by_id: {str(e)}")
            raise DatabaseException(f"Ошибка при получении {self.model_class.__name__} с ID {id}")
    
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
            self.logger.error(f"Database error in get_all: {str(e)}")
            raise DatabaseException(f"Ошибка при получении списка {self.model_class.__name__}")
    
    async def create(self, entity: Union[T, Dict[str, Any]]) -> T:
        """
        Создать новый объект
        
        Args:
            entity: Объект модели или словарь с данными для создания
            
        Returns:
            T: Созданный объект
        """
        try:
            # Если передан словарь, создаем объект модели
            if isinstance(entity, dict):
                entity = self.model_class(**entity)
            
            self.db.add(entity)
            await self.db.flush()  # Flush вместо commit для получения ID
            await self.db.refresh(entity)
            return entity
        except IntegrityError as e:
            self.logger.error(f"Integrity error in create: {str(e)}")
            raise IntegrityException(f"Нарушение целостности при создании {self.model_class.__name__}")
        except SQLAlchemyError as e:
            self.logger.error(f"Database error in create: {str(e)}")
            raise DatabaseException(f"Ошибка при создании {self.model_class.__name__}")
    
    async def update(self, entity: T) -> T:
        """Обновить существующий объект"""
        try:
            await self.db.flush()  # Flush вместо commit
            await self.db.refresh(entity)
            return entity
        except IntegrityError as e:
            self.logger.error(f"Integrity error in update: {str(e)}")
            raise IntegrityException(f"Нарушение целостности при обновлении {self.model_class.__name__}")
        except SQLAlchemyError as e:
            self.logger.error(f"Database error in update: {str(e)}")
            raise DatabaseException(f"Ошибка при обновлении {self.model_class.__name__}")
    
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
            self.logger.error(f"Database error in delete: {str(e)}")
            raise DatabaseException(f"Ошибка при удалении {self.model_class.__name__}")
    
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
            self.logger.error(f"Database error in count: {str(e)}")
            raise DatabaseException(f"Ошибка при подсчёте {self.model_class.__name__}")
    
    async def exists(self, id: int) -> bool:
        """Проверить существование объекта по ID"""
        try:
            result = await self.db.execute(
                select(func.count(self.model_class.id)).where(self.model_class.id == id)
            )
            return result.scalar() > 0
        except SQLAlchemyError as e:
            self.logger.error(f"Database error in exists: {str(e)}")
            raise DatabaseException(f"Ошибка при проверке существования {self.model_class.__name__}")
    
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
            self.logger.error(f"Database error in get_with_limit: {str(e)}")
            raise DatabaseException(f"Ошибка при получении {self.model_class.__name__} с пагинацией")
