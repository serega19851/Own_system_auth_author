from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.exc import SQLAlchemyError

from .base_repository import BaseRepository
from ..models.permission import Permission


class PermissionRepository(BaseRepository[Permission]):
    """
    Специализированный репозиторий для работы с разрешениями
    Расширяет базовый репозиторий дополнительными методами для работы с ресурсами
    """
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, Permission)
    
    async def get_by_names(self, perm_names: List[str]) -> List[Permission]:
        """
        Получить разрешения по списку названий
        
        Args:
            perm_names: Список названий разрешений
            
        Returns:
            List[Permission]: Список найденных разрешений
        """
        try:
            result = await self.db.execute(
                select(Permission).where(Permission.name.in_(perm_names))
            )
            return result.scalars().all()
        except SQLAlchemyError as e:
            
            raise e
    
    async def get_by_name(self, perm_name: str) -> Optional[Permission]:
        """
        Получить разрешение по названию
        
        Args:
            perm_name: Название разрешения
            
        Returns:
            Optional[Permission]: Разрешение или None
        """
        try:
            result = await self.db.execute(
                select(Permission).where(Permission.name == perm_name)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            
            raise e
    
    async def get_ordered_by_resource_type(self) -> List[Permission]:
        """
        Получить все разрешения, отсортированные по типу ресурса
        
        Returns:
            List[Permission]: Список разрешений, отсортированных по resource_type
        """
        try:
            result = await self.db.execute(
                select(Permission).order_by(Permission.resource_type, Permission.action)
            )
            return result.scalars().all()
        except SQLAlchemyError as e:
            
            raise e
    
    async def get_by_resource_type(self, resource_type: str) -> List[Permission]:
        """
        Получить разрешения по типу ресурса
        
        Args:
            resource_type: Тип ресурса (documents, reports, etc.)
            
        Returns:
            List[Permission]: Список разрешений для указанного типа ресурса
        """
        try:
            result = await self.db.execute(
                select(Permission)
                .where(Permission.resource_type == resource_type)
                .order_by(Permission.action)
            )
            return result.scalars().all()
        except SQLAlchemyError as e:
            
            raise e
    
    async def get_by_action(self, action: str) -> List[Permission]:
        """
        Получить разрешения по действию
        
        Args:
            action: Действие (read, write, create, delete, etc.)
            
        Returns:
            List[Permission]: Список разрешений для указанного действия
        """
        try:
            result = await self.db.execute(
                select(Permission)
                .where(Permission.action == action)
                .order_by(Permission.resource_type)
            )
            return result.scalars().all()
        except SQLAlchemyError as e:
            
            raise e
    
    async def get_by_resource_and_action(self, resource_type: str, action: str) -> Optional[Permission]:
        """
        Получить разрешение по типу ресурса и действию
        
        Args:
            resource_type: Тип ресурса
            action: Действие
            
        Returns:
            Optional[Permission]: Разрешение или None
        """
        try:
            result = await self.db.execute(
                select(Permission).where(
                    (Permission.resource_type == resource_type) &
                    (Permission.action == action)
                )
            )
            return result.scalar_one_or_none()
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
                select(Permission.resource_type).distinct().order_by(Permission.resource_type)
            )
            return [row[0] for row in result.fetchall()]
        except SQLAlchemyError as e:
            
            raise e
    
    async def get_unique_actions(self) -> List[str]:
        """
        Получить список уникальных действий
        
        Returns:
            List[str]: Список уникальных действий
        """
        try:
            result = await self.db.execute(
                select(Permission.action).distinct().order_by(Permission.action)
            )
            return [row[0] for row in result.fetchall()]
        except SQLAlchemyError as e:
            
            raise e
    
    async def search_permissions(self, search_term: str) -> List[Permission]:
        """
        Поиск разрешений по названию, типу ресурса или действию
        
        Args:
            search_term: Поисковый запрос
            
        Returns:
            List[Permission]: Список найденных разрешений
        """
        try:
            search_pattern = f"%{search_term}%"
            result = await self.db.execute(
                select(Permission).where(
                    (Permission.name.ilike(search_pattern)) |
                    (Permission.resource_type.ilike(search_pattern)) |
                    (Permission.action.ilike(search_pattern)) |
                    (Permission.description.ilike(search_pattern))
                ).order_by(Permission.resource_type, Permission.action)
            )
            return result.scalars().all()
        except SQLAlchemyError as e:
            
            raise e
    
    async def get_permissions_count_by_resource_type(self) -> List[dict]:
        """
        Получить статистику количества разрешений по типам ресурсов
        
        Returns:
            List[dict]: Список словарей с resource_type и count
        """
        try:
            result = await self.db.execute(
                select(
                    Permission.resource_type,
                    func.count(Permission.id).label('count')
                )
                .group_by(Permission.resource_type)
                .order_by(Permission.resource_type)
            )
            return [
                {"resource_type": row.resource_type, "count": row.count}
                for row in result.fetchall()
            ]
        except SQLAlchemyError as e:
            
            raise e
    
    async def check_permission_exists(self, resource_type: str, action: str) -> bool:
        """
        Проверить существование разрешения по типу ресурса и действию
        
        Args:
            resource_type: Тип ресурса
            action: Действие
            
        Returns:
            bool: True если разрешение существует
        """
        try:
            result = await self.db.execute(
                select(func.count(Permission.id)).where(
                    (Permission.resource_type == resource_type) &
                    (Permission.action == action)
                )
            )
            return result.scalar() > 0
        except SQLAlchemyError as e:
            
            raise e
