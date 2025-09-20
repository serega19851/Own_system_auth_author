"""
Сервис для управления ролями в админ-панели
Инкапсулирует логику работы с ролями для административных операций
"""

from typing import List
from datetime import datetime

from ...repositories.role_repository import RoleRepository
from ...repositories.permission_repository import PermissionRepository
from ...validators.system_validators import SystemValidators
from ...mappers.system_mappers import SystemMappers
from ...schemas.admin import RoleResponse, RoleCreate
from ...models.role import Role


class RoleManagementService:
    """
    Сервис для управления ролями в контексте админ-панели
    Содержит всю бизнес-логику для операций с ролями
    """
    
    def __init__(
        self,
        role_repo: RoleRepository,
        permission_repo: PermissionRepository,
        validators: SystemValidators,
        mappers: SystemMappers
    ):
        self.role_repo = role_repo
        self.permission_repo = permission_repo
        self.validators = validators
        self.mappers = mappers
    
    async def get_all_roles(self) -> List[RoleResponse]:
        """
        Получить все роли с их разрешениями для админ-панели
        
        Returns:
            List[RoleResponse]: Список ролей с разрешениями
        """
        # Получаем роли с предзагруженными разрешениями
        roles = await self.role_repo.get_roles_with_permissions()
        
        # Преобразуем в схемы ответа
        return self.mappers.roles_to_responses(roles)
    
    async def get_roles_with_pagination(
        self, 
        page: int = 1, 
        size: int = 20
    ) -> List[RoleResponse]:
        """
        Получить роли с пагинацией
        
        Args:
            page: Номер страницы (начиная с 1)
            size: Размер страницы
            
        Returns:
            List[RoleResponse]: Список ролей с разрешениями
        """
        offset = (page - 1) * size
        
        # Получаем роли с пагинацией
        roles = await self.role_repo.get_with_limit(
            limit=size, 
            offset=offset
        )
        
        # Для каждой роли загружаем разрешения
        roles_with_permissions = []
        for role in roles:
            role_with_permissions = await self.role_repo.get_role_with_permissions(role.id)
            if role_with_permissions:
                roles_with_permissions.append(role_with_permissions)
        
        return self.mappers.roles_to_responses(roles_with_permissions)
    
    async def create_role(self, role_data: RoleCreate) -> RoleResponse:
        """
        Создать новую роль с разрешениями
        
        Args:
            role_data: Данные для создания роли
            
        Returns:
            RoleResponse: Созданная роль с разрешениями
            
        Raises:
            RoleAlreadyExistsException: Если роль уже существует
            PermissionNotFoundException: Если какое-то разрешение не найдено
            ValueError: Если формат данных некорректен
        """
        # Валидируем формат названия роли
        self.validators.validate_role_name_format(role_data.name)
        
        # Проверяем уникальность названия роли
        await self.validators.validate_role_name_unique(role_data.name, self.role_repo)
        
        # Проверяем существование всех разрешений
        if role_data.permission_names:
            await self.validators.validate_permissions_exist(
                role_data.permission_names, 
                self.permission_repo
            )
        
        # Создаем новую роль
        new_role = Role(
            name=role_data.name.strip(),
            description=role_data.description,
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        # Сохраняем роль в БД
        created_role = await self.role_repo.create(new_role)
        
        # Назначаем разрешения роли если они указаны
        if role_data.permission_names:
            permissions = await self.permission_repo.get_by_names(role_data.permission_names)
            permission_ids = [perm.id for perm in permissions]
            await self.role_repo.assign_permissions(created_role.id, permission_ids)
        
        # Коммитим транзакцию
        await self.role_repo.db.commit()
        
        # Получаем созданную роль с разрешениями
        role_with_permissions = await self.role_repo.get_role_with_permissions(created_role.id)
        
        return self.mappers.role_to_response(role_with_permissions)
    
    async def validate_and_create_role(self, role_data: RoleCreate) -> RoleResponse:
        """
        Валидировать и создать роль
        
        Args:
            role_data: Данные для создания роли
            
        Returns:
            RoleResponse: Созданная роль
        """
        return await self.create_role(role_data)
    
    async def assign_permissions_to_role(
        self, 
        role_id: int, 
        permission_names: List[str]
    ) -> RoleResponse:
        """
        Назначить разрешения роли
        
        Args:
            role_id: ID роли
            permission_names: Список названий разрешений
            
        Returns:
            RoleResponse: Роль с обновленными разрешениями
            
        Raises:
            RoleNotFoundException: Если роль не найдена
            PermissionNotFoundException: Если какое-то разрешение не найдено
            InvalidRoleAssignmentException: Если назначение некорректно
        """
        # Валидируем назначение разрешений
        self.validators.validate_permission_assignment(role_id, permission_names)
        
        # Проверяем существование роли
        role = await self.role_repo.get_by_id(role_id)
        if not role:
            raise Exception(f"Роль с ID {role_id} не найдена")
        
        # Проверяем существование всех разрешений
        await self.validators.validate_permissions_exist(permission_names, self.permission_repo)
        
        # Получаем разрешения по названиям
        permissions = await self.permission_repo.get_by_names(permission_names)
        permission_ids = [perm.id for perm in permissions]
        
        # Назначаем разрешения роли
        success = await self.role_repo.assign_permissions(role_id, permission_ids)
        
        if not success:
            raise Exception("Не удалось назначить разрешения роли")
        
        # Получаем обновленную роль с разрешениями
        updated_role = await self.role_repo.get_role_with_permissions(role_id)
        
        return self.mappers.role_to_response(updated_role)
    
    async def add_permissions_to_role(
        self, 
        role_id: int, 
        permission_names: List[str]
    ) -> RoleResponse:
        """
        Добавить разрешения к роли (не заменяя существующие)
        
        Args:
            role_id: ID роли
            permission_names: Список названий разрешений для добавления
            
        Returns:
            RoleResponse: Роль с обновленными разрешениями
        """
        # Проверяем существование роли и разрешений
        role = await self.role_repo.get_by_id(role_id)
        if not role:
            raise Exception(f"Роль с ID {role_id} не найдена")
        
        await self.validators.validate_permissions_exist(permission_names, self.permission_repo)
        
        # Получаем разрешения по названиям
        permissions = await self.permission_repo.get_by_names(permission_names)
        permission_ids = [perm.id for perm in permissions]
        
        # Добавляем разрешения к роли
        success = await self.role_repo.add_permissions(role_id, permission_ids)
        
        if not success:
            raise Exception("Не удалось добавить разрешения к роли")
        
        # Получаем обновленную роль с разрешениями
        updated_role = await self.role_repo.get_role_with_permissions(role_id)
        
        return self.mappers.role_to_response(updated_role)
    
    async def remove_permissions_from_role(
        self, 
        role_id: int, 
        permission_names: List[str]
    ) -> RoleResponse:
        """
        Удалить разрешения у роли
        
        Args:
            role_id: ID роли
            permission_names: Список названий разрешений для удаления
            
        Returns:
            RoleResponse: Роль с обновленными разрешениями
        """
        # Проверяем существование роли
        role = await self.role_repo.get_by_id(role_id)
        if not role:
            raise Exception(f"Роль с ID {role_id} не найдена")
        
        # Получаем разрешения по названиям
        permissions = await self.permission_repo.get_by_names(permission_names)
        permission_ids = [perm.id for perm in permissions]
        
        # Удаляем разрешения у роли
        success = await self.role_repo.remove_permissions(role_id, permission_ids)
        
        if not success:
            raise Exception("Не удалось удалить разрешения у роли")
        
        # Получаем обновленную роль с разрешениями
        updated_role = await self.role_repo.get_role_with_permissions(role_id)
        
        return self.mappers.role_to_response(updated_role)
    
    async def get_role_details(self, role_id: int) -> RoleResponse:
        """
        Получить детальную информацию о роли
        
        Args:
            role_id: ID роли
            
        Returns:
            RoleResponse: Детальная информация о роли
            
        Raises:
            RoleNotFoundException: Если роль не найдена
        """
        # Получаем роль с разрешениями
        role = await self.role_repo.get_role_with_permissions(role_id)
        
        if not role:
            raise Exception(f"Роль с ID {role_id} не найдена")
        
        return self.mappers.role_to_response(role)
    
    async def get_role_by_name(self, role_name: str) -> RoleResponse:
        """
        Получить роль по названию
        
        Args:
            role_name: Название роли
            
        Returns:
            RoleResponse: Информация о роли
            
        Raises:
            RoleNotFoundException: Если роль не найдена
        """
        # Проверяем существование роли
        await self.validators.validate_roles_exist([role_name], self.role_repo)
        
        # Получаем роль по названию
        role = await self.role_repo.get_by_name(role_name)
        
        # Загружаем разрешения для роли
        role_with_permissions = await self.role_repo.get_role_with_permissions(role.id)
        
        return self.mappers.role_to_response(role_with_permissions)
    
    async def get_role_statistics_summary(self) -> dict:
        """
        Получить краткую статистику ролей
        
        Returns:
            dict: Статистика ролей
        """
        total_roles = await self.role_repo.count()
        active_roles = await self.role_repo.get_active_roles_count()
        inactive_roles = await self.role_repo.get_inactive_roles_count()
        
        return {
            "total": total_roles,
            "active": active_roles,
            "inactive": inactive_roles,
            "percentage_active": round((active_roles / total_roles * 100) if total_roles > 0 else 0, 2)
        }
