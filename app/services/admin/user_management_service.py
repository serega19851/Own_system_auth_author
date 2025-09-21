"""
Сервис для управления пользователями в админ-панели
Инкапсулирует логику работы с пользователями для административных операций
"""

from typing import List, Optional

from ...repositories.user_repository import UserRepository
from ...repositories.role_repository import RoleRepository
from ...validators.system_validators import SystemValidators
from ...mappers.system_mappers import SystemMappers
from ...schemas.admin import UserListItem, UserRoleUpdate


from ..base_service import BaseService
from ...exceptions.business_exceptions import UserException

class UserManagementService(BaseService):
    """
    Сервис для управления пользователями в контексте админ-панели
    Содержит всю бизнес-логику для операций с пользователями
    """
    
    def __init__(
        self,
        user_repo: UserRepository,
        role_repo: RoleRepository,
        validators: SystemValidators,
        mappers: SystemMappers
    ):
        super().__init__()
        self.user_repo = user_repo
        self.role_repo = role_repo
        self.validators = validators
        self.mappers = mappers
    
    async def get_all_users(self) -> List[UserListItem]:
        """
        Получить всех пользователей с их ролями для админ-панели
        
        Returns:
            List[UserListItem]: Список пользователей с ролями
        """
        try:
            # Получаем пользователей с предзагруженными ролями
            users = await self.user_repo.get_users_with_roles()
            
            # Преобразуем в схемы ответа
            return self.mappers.users_to_list_items(users)
        except Exception as e:
            self._handle_service_error(e, "get_all_users")
            raise
    
    async def get_users_with_pagination(
        self, 
        page: int = 1, 
        size: int = 20
    ) -> List[UserListItem]:
        """
        Получить пользователей с пагинацией
        
        Args:
            page: Номер страницы (начиная с 1)
            size: Размер страницы
            
        Returns:
            List[UserListItem]: Список пользователей с ролями
        """
        try:
            offset = (page - 1) * size
            
            # Получаем пользователей с пагинацией
            users = await self.user_repo.get_with_limit(
                limit=size, 
                offset=offset
            )
            
            # Для каждого пользователя загружаем роли
            users_with_roles = []
            for user in users:
                user_with_roles = await self.user_repo.get_user_with_roles(user.id)
                if user_with_roles:
                    users_with_roles.append(user_with_roles)
            
            return self.mappers.users_to_list_items(users_with_roles)
        except Exception as e:
            self._handle_service_error(e, "get_users_with_pagination")
            raise
    
    async def filter_users(
        self, 
        is_active: Optional[bool] = None, 
        role_name: Optional[str] = None
    ) -> List[UserListItem]:
        """
        Получить пользователей с фильтрацией
        
        Args:
            is_active: Фильтр по активности пользователей
            role_name: Фильтр по названию роли
            
        Returns:
            List[UserListItem]: Отфильтрованный список пользователей
        """
        try:
            if role_name:
                # Получаем пользователей с определенной ролью
                users = await self.user_repo.get_users_by_role(role_name)
                
                # Дополнительно фильтруем по активности если нужно
                if is_active is not None:
                    users = [user for user in users if user.is_active == is_active]
            else:
                # Получаем всех пользователей с фильтром по активности
                if is_active is not None:
                    users = await self.user_repo.get_all(is_active=is_active)
                    # Загружаем роли для каждого пользователя
                    users_with_roles = []
                    for user in users:
                        user_with_roles = await self.user_repo.get_user_with_roles(user.id)
                        if user_with_roles:
                            users_with_roles.append(user_with_roles)
                    users = users_with_roles
                else:
                    # Получаем всех пользователей с ролями
                    users = await self.user_repo.get_users_with_roles()
            
            return self.mappers.users_to_list_items(users)
        except Exception as e:
            self._handle_service_error(e, "filter_users")
            raise
    
    async def update_user_roles(
        self, 
        user_id: int, 
        role_update: UserRoleUpdate
    ) -> UserListItem:
        """
        Обновить роли пользователя
        
        Args:
            user_id: ID пользователя
            role_update: Данные для обновления ролей
            
        Returns:
            UserListItem: Обновленные данные пользователя
            
        Raises:
            UserNotFoundException: Если пользователь не найден
            RoleNotFoundException: Если какая-то роль не найдена
            InvalidRoleAssignmentException: Если назначение некорректно
        """
        try:
            # Валидируем входные данные
            self.validators.validate_role_assignment(user_id, role_update.role_names)
            
            # Проверяем существование пользователя
            await self.validators.validate_user_exists(user_id, self.user_repo)
            
            # Проверяем существование всех ролей
            await self.validators.validate_roles_exist(role_update.role_names, self.role_repo)
            
            # Получаем роли по названиям
            roles = await self.role_repo.get_by_names(role_update.role_names)
            role_ids = [role.id for role in roles]
            
            # Обновляем роли пользователя
            success = await self.user_repo.update_user_roles(user_id, role_ids)
            
            if not success:
                raise UserException("Не удалось обновить роли пользователя", "USER_ROLES_UPDATE_FAILED")
            
            # Получаем обновленного пользователя с ролями
            updated_user = await self.user_repo.get_user_with_roles(user_id)
            
            return self.mappers.user_to_list_item(updated_user)
        except Exception as e:
            self._handle_service_error(e, "update_user_roles")
            raise
    
    async def validate_and_update_roles(
        self, 
        user_id: int, 
        role_names: List[str]
    ) -> UserListItem:
        """
        Валидировать и обновить роли пользователя
        
        Args:
            user_id: ID пользователя
            role_names: Список названий ролей
            
        Returns:
            UserListItem: Обновленные данные пользователя
        """
        try:
            role_update = UserRoleUpdate(role_names=role_names)
            return await self.update_user_roles(user_id, role_update)
        except Exception as e:
            self._handle_service_error(e, "validate_and_update_roles")
            raise
    
    async def search_users(
        self, 
        search_term: str, 
        limit: int = 20
    ) -> List[UserListItem]:
        """
        Поиск пользователей по имени или email
        
        Args:
            search_term: Поисковый запрос
            limit: Максимальное количество результатов
            
        Returns:
            List[UserListItem]: Найденные пользователи с ролями
        """
        try:
            users = await self.user_repo.search_users(search_term, limit)
            return self.mappers.users_to_list_items(users)
        except Exception as e:
            self._handle_service_error(e, "search_users")
            raise
    
    async def get_user_details(self, user_id: int) -> UserListItem:
        """
        Получить детальную информацию о пользователе
        
        Args:
            user_id: ID пользователя
            
        Returns:
            UserListItem: Детальная информация о пользователе
            
        Raises:
            UserNotFoundException: Если пользователь не найден
        """
        try:
            # Проверяем существование пользователя
            await self.validators.validate_user_exists(user_id, self.user_repo)
            
            # Получаем пользователя с ролями
            user = await self.user_repo.get_user_with_roles(user_id)
            
            return self.mappers.user_to_list_item(user)
        except Exception as e:
            self._handle_service_error(e, "get_user_details")
            raise
    
    async def get_users_by_role(self, role_name: str) -> List[UserListItem]:
        """
        Получить пользователей с определенной ролью
        
        Args:
            role_name: Название роли
            
        Returns:
            List[UserListItem]: Пользователи с указанной ролью
            
        Raises:
            RoleNotFoundException: Если роль не найдена
        """
        try:
            # Проверяем существование роли
            await self.validators.validate_roles_exist([role_name], self.role_repo)
            
            # Получаем пользователей с ролью
            users = await self.user_repo.get_users_by_role(role_name)
            
            return self.mappers.users_to_list_items(users)
        except Exception as e:
            self._handle_service_error(e, "get_users_by_role")
            raise
    
    async def get_user_statistics_summary(self) -> dict:
        """
        Получить краткую статистику пользователей
        
        Returns:
            dict: Статистика пользователей
        """
        try:
            total_users = await self.user_repo.count()
            active_users = await self.user_repo.get_active_users_count()
            inactive_users = await self.user_repo.get_inactive_users_count()
            
            return {
                "total": total_users,
                "active": active_users,
                "inactive": inactive_users,
                "percentage_active": round((active_users / total_users * 100) if total_users > 0 else 0, 2)
            }
        except Exception as e:
            self._handle_service_error(e, "get_user_statistics_summary")
            raise
