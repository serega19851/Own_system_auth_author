"""
Валидаторы для проверки бизнес-правил системы
Содержит статические методы для валидации данных перед операциями
"""

from typing import List
from ..repositories.user_repository import UserRepository
from ..repositories.role_repository import RoleRepository
from ..repositories.permission_repository import PermissionRepository
from ..exceptions.validator_exceptions import (
    UserNotFoundException, RoleNotFoundException, RoleAlreadyExistsException,
    PermissionNotFoundException, InvalidRoleAssignmentException
)


class SystemValidators:
    """
    Класс для валидации бизнес-правил системы
    Содержит статические методы для проверки данных
    """
    
    @staticmethod
    async def validate_user_exists(user_id: int, user_repo: UserRepository) -> None:
        """
        Проверить существование пользователя
        
        Args:
            user_id: ID пользователя
            user_repo: Репозиторий пользователей
            
        Raises:
            UserNotFoundException: Если пользователь не найден
        """
        user = await user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundException(f"Пользователь с ID {user_id} не найден")
        
        if not user.is_active:
            raise UserNotFoundException(f"Пользователь с ID {user_id} неактивен")
    
    @staticmethod
    async def validate_roles_exist(role_names: List[str], role_repo: RoleRepository) -> None:
        """
        Проверить существование ролей по названиям
        
        Args:
            role_names: Список названий ролей
            role_repo: Репозиторий ролей
            
        Raises:
            RoleNotFoundException: Если какая-то роль не найдена
        """
        if not role_names:
            return
            
        existing_roles = await role_repo.get_by_names(role_names)
        existing_role_names = {role.name for role in existing_roles}
        
        missing_roles = set(role_names) - existing_role_names
        if missing_roles:
            raise RoleNotFoundException(
                f"Роли не найдены: {', '.join(missing_roles)}"
            )
        
        # Проверяем активность ролей
        inactive_roles = [
            role.name for role in existing_roles 
            if not role.is_active
        ]
        if inactive_roles:
            raise RoleNotFoundException(
                f"Роли неактивны: {', '.join(inactive_roles)}"
            )
    
    @staticmethod
    async def validate_permissions_exist(perm_names: List[str], perm_repo: PermissionRepository) -> None:
        """
        Проверить существование разрешений по названиям
        
        Args:
            perm_names: Список названий разрешений
            perm_repo: Репозиторий разрешений
            
        Raises:
            PermissionNotFoundException: Если какое-то разрешение не найдено
        """
        if not perm_names:
            return
            
        existing_permissions = await perm_repo.get_by_names(perm_names)
        existing_perm_names = {perm.name for perm in existing_permissions}
        
        missing_permissions = set(perm_names) - existing_perm_names
        if missing_permissions:
            raise PermissionNotFoundException(
                f"Разрешения не найдены: {', '.join(missing_permissions)}"
            )
    
    @staticmethod
    async def validate_role_name_unique(name: str, role_repo: RoleRepository) -> None:
        """
        Проверить уникальность названия роли
        
        Args:
            name: Название роли
            role_repo: Репозиторий ролей
            
        Raises:
            RoleAlreadyExistsException: Если роль уже существует
        """
        exists = await role_repo.check_role_exists(name)
        if exists:
            raise RoleAlreadyExistsException(f"Роль с названием '{name}' уже существует")
    
    @staticmethod
    def validate_role_name_format(name: str) -> None:
        """
        Проверить формат названия роли
        
        Args:
            name: Название роли
            
        Raises:
            ValueError: Если формат названия некорректен
        """
        if not name or not name.strip():
            raise ValueError("Название роли не может быть пустым")
        
        if len(name.strip()) < 2:
            raise ValueError("Название роли должно содержать минимум 2 символа")
        
        if len(name.strip()) > 50:
            raise ValueError("Название роли не должно превышать 50 символов")
        
        # Проверяем допустимые символы (буквы, цифры, подчеркивания, дефисы)
        allowed_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-")
        if not all(c in allowed_chars for c in name.strip()):
            raise ValueError("Название роли может содержать только буквы, цифры, подчеркивания и дефисы")
    
    @staticmethod
    def validate_role_assignment(user_id: int, role_names: List[str]) -> None:
        """
        Проверить корректность назначения ролей пользователю
        
        Args:
            user_id: ID пользователя
            role_names: Список названий ролей
            
        Raises:
            InvalidRoleAssignmentException: Если назначение некорректно
        """
        if user_id <= 0:
            raise InvalidRoleAssignmentException("ID пользователя должен быть положительным числом")
        
        if not role_names:
            raise InvalidRoleAssignmentException("Список ролей не может быть пустым")
        
        # Проверяем на дубликаты
        if len(role_names) != len(set(role_names)):
            raise InvalidRoleAssignmentException("В списке ролей есть дубликаты")
        
        # Проверяем максимальное количество ролей на пользователя
        if len(role_names) > 10:
            raise InvalidRoleAssignmentException("Пользователю нельзя назначить более 10 ролей")
    
    @staticmethod
    def validate_permission_assignment(role_id: int, permission_names: List[str]) -> None:
        """
        Проверить корректность назначения разрешений роли
        
        Args:
            role_id: ID роли
            permission_names: Список названий разрешений
            
        Raises:
            InvalidRoleAssignmentException: Если назначение некорректно
        """
        if role_id <= 0:
            raise InvalidRoleAssignmentException("ID роли должен быть положительным числом")
        
        if not permission_names:
            return  # Роль может существовать без разрешений
        
        # Проверяем на дубликаты
        if len(permission_names) != len(set(permission_names)):
            raise InvalidRoleAssignmentException("В списке разрешений есть дубликаты")
        
        # Проверяем максимальное количество разрешений на роль
        if len(permission_names) > 50:
            raise InvalidRoleAssignmentException("Роли нельзя назначить более 50 разрешений")
    
    @staticmethod
    async def validate_user_can_be_updated(user_id: int, user_repo: UserRepository) -> None:
        """
        Проверить возможность обновления пользователя
        
        Args:
            user_id: ID пользователя
            user_repo: Репозиторий пользователей
            
        Raises:
            UserNotFoundException: Если пользователь не найден
            InvalidRoleAssignmentException: Если пользователя нельзя обновить
        """
        user = await user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundException(f"Пользователь с ID {user_id} не найден")
        
        # Дополнительные проверки можно добавить здесь
        # Например, проверка на системных пользователей, которых нельзя изменять
