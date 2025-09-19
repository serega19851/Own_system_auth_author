from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.exc import SQLAlchemyError

from .base_repository import BaseRepository
from ..models.resource import Resource


class ResourceRepository(BaseRepository[Resource]):
    """
    Специализированный репозиторий для работы с ресурсами
    Расширяет базовый репозиторий дополнительными методами
    """
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, Resource)
    
    async def get_by_resource_type(self, resource_type: str) -> List[Resource]:
        """
        Получить ресурсы по типу
        
        Args:
            resource_type: Тип ресурса
            
        Returns:
            List[Resource]: Список ресурсов указанного типа
        """
        try:
            result = await self.db.execute(
                select(Resource)
                .where(Resource.resource_type == resource_type)
                .order_by(Resource.name)
            )
            return result.scalars().all()
        except SQLAlchemyError as e:
            
            raise e
    
    async def get_active_resources(self) -> List[Resource]:
        """
        Получить все активные ресурсы
        
        Returns:
            List[Resource]: Список активных ресурсов
        """
        try:
            result = await self.db.execute(
                select(Resource)
                .where(Resource.is_active == True)
                .order_by(Resource.resource_type, Resource.name)
            )
            return result.scalars().all()
        except SQLAlchemyError as e:
            
            raise e
    
    async def get_unique_resource_types(self) -> List[str]:
        """
        Получить список уникальных типов ресурсов
        
        Returns:
            List[str]: Список уникальных типов ресурсов
        """
        try:
            result = await self.db.execute(
                select(Resource.resource_type).distinct().order_by(Resource.resource_type)
            )
            return [row[0] for row in result.fetchall()]
        except SQLAlchemyError as e:
            
            raise e
    
    async def get_active_resources_count(self) -> int:
        """
        Получить количество активных ресурсов
        
        Returns:
            int: Количество активных ресурсов
        """
        try:
            result = await self.db.execute(
                select(func.count(Resource.id)).where(Resource.is_active == True)
            )
            return result.scalar()
        except SQLAlchemyError as e:
            
            raise e
    
    async def get_inactive_resources_count(self) -> int:
        """
        Получить количество неактивных ресурсов
        
        Returns:
            int: Количество неактивных ресурсов
        """
        try:
            result = await self.db.execute(
                select(func.count(Resource.id)).where(Resource.is_active == False)
            )
            return result.scalar()
        except SQLAlchemyError as e:
            
            raise e
    
    async def get_resources_count_by_type(self) -> List[dict]:
        """
        Получить статистику количества ресурсов по типам
        
        Returns:
            List[dict]: Список словарей с resource_type и count
        """
        try:
            result = await self.db.execute(
                select(
                    Resource.resource_type,
                    func.count(Resource.id).label('count')
                )
                .group_by(Resource.resource_type)
                .order_by(Resource.resource_type)
            )
            return [
                {"resource_type": row.resource_type, "count": row.count}
                for row in result.fetchall()
            ]
        except SQLAlchemyError as e:
            
            raise e
    
    async def search_resources(self, search_term: str) -> List[Resource]:
        """
        Поиск ресурсов по названию или описанию
        
        Args:
            search_term: Поисковый запрос
            
        Returns:
            List[Resource]: Список найденных ресурсов
        """
        try:
            search_pattern = f"%{search_term}%"
            result = await self.db.execute(
                select(Resource).where(
                    (Resource.name.ilike(search_pattern)) |
                    (Resource.description.ilike(search_pattern)) |
                    (Resource.resource_type.ilike(search_pattern))
                ).order_by(Resource.resource_type, Resource.name)
            )
            return result.scalars().all()
        except SQLAlchemyError as e:
            
            raise e
