from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError

from .base_repository import BaseRepository
from ..models.role import Role
from ..models.permission import Permission
from ..models.associations import role_permissions


class RoleRepository(BaseRepository[Role]):
    """
    Специализированный репозиторий для работы с ролями
    Расширяет базовый репозиторий дополнительными методами для работы с разрешениями
    """
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, Role)
    
    async def get_roles_with_permissions(self) -> List[Role]:
        """
        Получить все роли с загруженными разрешениями
        
        Returns:
            List[Role]: Список ролей с разрешениями
        """
        try:
            result = await self.db.execute(
                select(Role).options(selectinload(Role.permissions))
            )
            return result.scalars().all()
        except SQLAlchemyError as e:
            
            raise e
    
    async def get_role_with_permissions(self, role_id: int) -> Optional[Role]:
        """
        Получить роль по ID с загруженными разрешениями
        
        Args:
            role_id: ID роли
            
        Returns:
            Optional[Role]: Роль с разрешениями или None
        """
        try:
            result = await self.db.execute(
                select(Role)
                .options(selectinload(Role.permissions))
                .where(Role.id == role_id)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            
            raise e
    
    async def get_by_names(self, role_names: List[str]) -> List[Role]:
        """
        Получить роли по списку названий
        
        Args:
            role_names: Список названий ролей
            
        Returns:
            List[Role]: Список найденных ролей
        """
        try:
            result = await self.db.execute(
                select(Role).where(Role.name.in_(role_names))
            )
            return result.scalars().all()
        except SQLAlchemyError as e:
            
            raise e
    
    async def get_by_name(self, role_name: str) -> Optional[Role]:
        """
        Получить роль по названию
        
        Args:
            role_name: Название роли
            
        Returns:
            Optional[Role]: Роль или None
        """
        try:
            result = await self.db.execute(
                select(Role).where(Role.name == role_name)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            
            raise e
    
    async def assign_permissions(self, role_id: int, permission_ids: List[int]) -> bool:
        """
        Назначить разрешения роли
        
        Args:
            role_id: ID роли
            permission_ids: Список ID разрешений
            
        Returns:
            bool: True если назначение прошло успешно
        """
        try:
            # Получаем роль с предзагруженными разрешениями
            role_result = await self.db.execute(
                select(Role).options(selectinload(Role.permissions)).where(Role.id == role_id)
            )
            role = role_result.scalar_one_or_none()
            if not role:
                return False
            
            # Получаем разрешения по ID
            permissions_result = await self.db.execute(
                select(Permission).where(Permission.id.in_(permission_ids))
            )
            permissions = permissions_result.scalars().all()
            
            # Назначаем разрешения роли (теперь без lazy loading)
            role.permissions = permissions
            await self.db.flush()
            return True
            
        except SQLAlchemyError as e:
            
            raise e
    
    async def add_permissions(self, role_id: int, permission_ids: List[int]) -> bool:
        """
        Добавить разрешения к роли (не заменяя существующие)
        
        Args:
            role_id: ID роли
            permission_ids: Список ID разрешений для добавления
            
        Returns:
            bool: True если добавление прошло успешно
        """
        try:
            # Получаем роль с существующими разрешениями
            role = await self.get_role_with_permissions(role_id)
            if not role:
                return False
            
            # Получаем новые разрешения
            new_permissions_result = await self.db.execute(
                select(Permission).where(Permission.id.in_(permission_ids))
            )
            new_permissions = new_permissions_result.scalars().all()
            
            # Добавляем новые разрешения к существующим
            existing_permission_ids = {p.id for p in role.permissions}
            for permission in new_permissions:
                if permission.id not in existing_permission_ids:
                    role.permissions.append(permission)
            
            await self.db.flush()
            return True
            
        except SQLAlchemyError as e:
            
            raise e
    
    async def remove_permissions(self, role_id: int, permission_ids: List[int]) -> bool:
        """
        Удалить разрешения у роли
        
        Args:
            role_id: ID роли
            permission_ids: Список ID разрешений для удаления
            
        Returns:
            bool: True если удаление прошло успешно
        """
        try:
            # Получаем роль с разрешениями
            role = await self.get_role_with_permissions(role_id)
            if not role:
                return False
            
            # Удаляем указанные разрешения
            role.permissions = [
                p for p in role.permissions 
                if p.id not in permission_ids
            ]
            
            await self.db.flush()
            return True
            
        except SQLAlchemyError as e:
            
            raise e
    
    async def check_role_exists(self, name: str) -> bool:
        """
        Проверить существование роли по названию
        
        Args:
            name: Название роли
            
        Returns:
            bool: True если роль существует
        """
        try:
            result = await self.db.execute(
                select(func.count(Role.id)).where(Role.name == name)
            )
            return result.scalar() > 0
        except SQLAlchemyError as e:
            
            raise e
    
    async def get_active_roles_count(self) -> int:
        """
        Получить количество активных ролей
        
        Returns:
            int: Количество активных ролей
        """
        try:
            result = await self.db.execute(
                select(func.count(Role.id)).where(Role.is_active == True)
            )
            return result.scalar()
        except SQLAlchemyError as e:
            
            raise e
    
    async def get_inactive_roles_count(self) -> int:
        """
        Получить количество неактивных ролей
        
        Returns:
            int: Количество неактивных ролей
        """
        try:
            result = await self.db.execute(
                select(func.count(Role.id)).where(Role.is_active == False)
            )
            return result.scalar()
        except SQLAlchemyError as e:
            
            raise e
