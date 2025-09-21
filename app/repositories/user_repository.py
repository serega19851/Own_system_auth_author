from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError

from .base_repository import BaseRepository
from ..models.user import User
from ..models.role import Role
from ..models.associations import user_roles
from ..exceptions.database_exceptions import DatabaseException


class UserRepository(BaseRepository[User]):
    """
    Специализированный репозиторий для работы с пользователями
    Расширяет базовый репозиторий дополнительными методами для работы с ролями
    """
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, User)
    
    async def get_users_with_roles(self) -> List[User]:
        """
        Получить всех пользователей с загруженными ролями
        
        Returns:
            List[User]: Список пользователей с ролями
        """
        try:
            result = await self.db.execute(
                select(User).options(selectinload(User.roles))
            )
            return result.scalars().all()
        except SQLAlchemyError as e:
            self.logger.error(f"Database error in get_users_with_roles: {str(e)}")
            raise DatabaseException("Ошибка при получении пользователей с ролями")
    
    async def get_user_with_roles(self, user_id: int) -> Optional[User]:
        """
        Получить пользователя по ID с загруженными ролями
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Optional[User]: Пользователь с ролями или None
        """
        try:
            result = await self.db.execute(
                select(User)
                .options(selectinload(User.roles))
                .where(User.id == user_id)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            self.logger.error(f"Database error in get_user_with_roles: {str(e)}")
            raise DatabaseException(f"Ошибка при получении пользователя {user_id} с ролями")
    
    async def update_user_roles(self, user_id: int, role_ids: List[int]) -> bool:
        """
        Обновить роли пользователя
        
        Args:
            user_id: ID пользователя
            role_ids: Список ID ролей для назначения
            
        Returns:
            bool: True если обновление прошло успешно
        """
        try:
            # Получаем пользователя с предзагруженными ролями
            user_result = await self.db.execute(
                select(User).options(selectinload(User.roles)).where(User.id == user_id)
            )
            user = user_result.scalar_one_or_none()
            if not user:
                return False
            
            # Получаем роли по ID
            roles_result = await self.db.execute(
                select(Role).where(Role.id.in_(role_ids))
            )
            roles = roles_result.scalars().all()
            
            # Обновляем роли пользователя (теперь без lazy loading)
            user.roles = roles
            await self.db.flush()  # Flush для применения изменений
            return True
            
        except SQLAlchemyError as e:
            self.logger.error(f"Database error in update_user_roles: {str(e)}")
            raise DatabaseException(f"Ошибка при обновлении ролей пользователя {user_id}")
    
    async def get_active_users_count(self) -> int:
        """
        Получить количество активных пользователей
        
        Returns:
            int: Количество активных пользователей
        """
        try:
            result = await self.db.execute(
                select(func.count(User.id)).where(User.is_active == True)
            )
            return result.scalar()
        except SQLAlchemyError as e:
            
            self.logger.error(f"Database error: {str(e)}")
            raise DatabaseException("Ошибка в операции с пользователями")
    
    async def get_inactive_users_count(self) -> int:
        """
        Получить количество неактивных пользователей
        
        Returns:
            int: Количество неактивных пользователей
        """
        try:
            result = await self.db.execute(
                select(func.count(User.id)).where(User.is_active == False)
            )
            return result.scalar()
        except SQLAlchemyError as e:
            
            self.logger.error(f"Database error: {str(e)}")
            raise DatabaseException("Ошибка в операции с пользователями")
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Получить пользователя по email
        
        Args:
            email: Email пользователя
            
        Returns:
            Optional[User]: Пользователь или None
        """
        try:
            result = await self.db.execute(
                select(User).where(User.email == email)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            
            self.logger.error(f"Database error: {str(e)}")
            raise DatabaseException("Ошибка в операции с пользователями")
    
    async def get_users_by_role(self, role_name: str) -> List[User]:
        """
        Получить пользователей с определенной ролью
        
        Args:
            role_name: Название роли
            
        Returns:
            List[User]: Список пользователей с указанной ролью
        """
        try:
            result = await self.db.execute(
                select(User)
                .join(user_roles)
                .join(Role)
                .where(Role.name == role_name)
                .options(selectinload(User.roles))
            )
            return result.scalars().all()
        except SQLAlchemyError as e:
            
            self.logger.error(f"Database error: {str(e)}")
            raise DatabaseException("Ошибка в операции с пользователями")
    
    async def search_users(self, search_term: str, limit: int = 20) -> List[User]:
        """
        Поиск пользователей по имени или email
        
        Args:
            search_term: Поисковый запрос
            limit: Максимальное количество результатов
            
        Returns:
            List[User]: Список найденных пользователей
        """
        try:
            search_pattern = f"%{search_term}%"
            result = await self.db.execute(
                select(User)
                .where(
                    (User.first_name.ilike(search_pattern)) |
                    (User.last_name.ilike(search_pattern)) |
                    (User.middle_name.ilike(search_pattern)) |
                    (User.email.ilike(search_pattern))
                )
                .options(selectinload(User.roles))
                .limit(limit)
            )
            return result.scalars().all()
        except SQLAlchemyError as e:
            
            self.logger.error(f"Database error: {str(e)}")
            raise DatabaseException("Ошибка в операции с пользователями")
    
    async def get_user_with_roles_and_permissions(self, user_id: int) -> Optional[User]:
        """
        Получить пользователя по ID с загруженными ролями и разрешениями
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Optional[User]: Пользователь с ролями и разрешениями или None
        """
        try:
            result = await self.db.execute(
                select(User)
                .options(
                    selectinload(User.roles).selectinload(Role.permissions)
                )
                .where(User.id == user_id)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            self.logger.error(f"Database error: {str(e)}")
            raise DatabaseException("Ошибка в операции с пользователями")
    
    async def update_user_profile_data(self, user_id: int, update_data: Dict[str, Any]) -> Optional[User]:
        """
        Обновить данные профиля пользователя
        
        Args:
            user_id: ID пользователя
            update_data: Словарь с данными для обновления
            
        Returns:
            Optional[User]: Обновленный пользователь или None
        """
        try:
            # Обновляем пользователя
            await self.db.execute(
                update(User)
                .where(User.id == user_id)
                .values(**update_data)
            )
            await self.db.commit()
            
            # Возвращаем обновленного пользователя
            return await self.get_by_id(user_id)
            
        except SQLAlchemyError as e:
            await self.db.rollback()
            self.logger.error(f"Database error: {str(e)}")
            raise DatabaseException("Ошибка в операции с пользователями")
    
    async def deactivate_user(self, user_id: int) -> bool:
        """
        Деактивировать пользователя (мягкое удаление)
        
        Args:
            user_id: ID пользователя
            
        Returns:
            bool: True если деактивация прошла успешно
        """
        try:
            result = await self.db.execute(
                update(User)
                .where(User.id == user_id)
                .values(
                    is_active=False,
                    updated_at=datetime.utcnow()
                )
            )
            await self.db.commit()
            
            # Проверяем, что строка была обновлена
            return result.rowcount > 0
            
        except SQLAlchemyError as e:
            await self.db.rollback()
            self.logger.error(f"Database error: {str(e)}")
            raise DatabaseException("Ошибка в операции с пользователями")
