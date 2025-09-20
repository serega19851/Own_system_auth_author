"""
Мапперы для преобразования моделей SQLAlchemy в схемы Pydantic
Централизованное место для всех преобразований данных
"""

from typing import List
from ..models.user import User
from ..models.role import Role
from ..models.permission import Permission
from ..schemas.admin import (
    UserListItem, 
    RoleResponse, 
    PermissionResponse,
    AdminStatsResponse
)
from ..schemas.user import UserProfile


class SystemMappers:
    """
    Класс для преобразования моделей SQLAlchemy в схемы Pydantic
    Содержит статические методы для каждого типа преобразования
    """
    
    @staticmethod
    def user_to_list_item(user: User) -> UserListItem:
        """
        Преобразовать пользователя в элемент списка для админ-панели
        
        Args:
            user: Модель пользователя с загруженными ролями
            
        Returns:
            UserListItem: Схема элемента списка пользователей
        """
        return UserListItem(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            middle_name=user.middle_name,
            is_active=user.is_active,
            created_at=user.created_at,
            roles=[role.name for role in user.roles] if user.roles else []
        )
    
    @staticmethod
    def role_to_response(role: Role) -> RoleResponse:
        """
        Преобразовать роль в схему ответа
        
        Args:
            role: Модель роли с загруженными разрешениями
            
        Returns:
            RoleResponse: Схема ответа роли
        """
        return RoleResponse(
            id=role.id,
            name=role.name,
            description=role.description,
            is_active=role.is_active,
            created_at=role.created_at,
            permissions=[perm.name for perm in role.permissions] if role.permissions else []
        )
    
    @staticmethod
    def permission_to_response(permission: Permission) -> PermissionResponse:
        """
        Преобразовать разрешение в схему ответа
        
        Args:
            permission: Модель разрешения
            
        Returns:
            PermissionResponse: Схема ответа разрешения
        """
        return PermissionResponse(
            id=permission.id,
            name=permission.name,
            resource_type=permission.resource_type,
            action=permission.action,
            description=permission.description
        )
    
    @staticmethod
    def users_to_list_items(users: List[User]) -> List[UserListItem]:
        """
        Преобразовать список пользователей в элементы списка
        
        Args:
            users: Список моделей пользователей с загруженными ролями
            
        Returns:
            List[UserListItem]: Список схем элементов пользователей
        """
        return [SystemMappers.user_to_list_item(user) for user in users]
    
    @staticmethod
    def roles_to_responses(roles: List[Role]) -> List[RoleResponse]:
        """
        Преобразовать список ролей в схемы ответов
        
        Args:
            roles: Список моделей ролей с загруженными разрешениями
            
        Returns:
            List[RoleResponse]: Список схем ответов ролей
        """
        return [SystemMappers.role_to_response(role) for role in roles]
    
    @staticmethod
    def permissions_to_responses(permissions: List[Permission]) -> List[PermissionResponse]:
        """
        Преобразовать список разрешений в схемы ответов
        
        Args:
            permissions: Список моделей разрешений
            
        Returns:
            List[PermissionResponse]: Список схем ответов разрешений
        """
        return [SystemMappers.permission_to_response(permission) for permission in permissions]
    
    @staticmethod
    def create_admin_stats_response(
        total_users: int,
        active_users: int,
        inactive_users: int,
        total_roles: int,
        total_permissions: int,
        total_resources: int
    ) -> AdminStatsResponse:
        """
        Создать схему статистики для админ-панели
        
        Args:
            total_users: Общее количество пользователей
            active_users: Количество активных пользователей
            inactive_users: Количество неактивных пользователей
            total_roles: Общее количество ролей
            total_permissions: Общее количество разрешений
            total_resources: Общее количество ресурсов
            
        Returns:
            AdminStatsResponse: Схема статистики админ-панели
        """
        return AdminStatsResponse(
            total_users=total_users,
            active_users=active_users,
            inactive_users=inactive_users,
            total_roles=total_roles,
            total_permissions=total_permissions,
            total_resources=total_resources
        )
    
    @staticmethod
    def extract_role_names(roles: List[Role]) -> List[str]:
        """
        Извлечь названия ролей из списка моделей
        
        Args:
            roles: Список моделей ролей
            
        Returns:
            List[str]: Список названий ролей
        """
        return [role.name for role in roles]
    
    @staticmethod
    def extract_permission_names(permissions: List[Permission]) -> List[str]:
        """
        Извлечь названия разрешений из списка моделей
        
        Args:
            permissions: Список моделей разрешений
            
        Returns:
            List[str]: Список названий разрешений
        """
        return [permission.name for permission in permissions]
    
    @staticmethod
    def user_to_profile(user: User) -> UserProfile:
        """
        Преобразовать пользователя в профиль (без разрешений)
        
        Args:
            user: Модель пользователя с загруженными ролями
            
        Returns:
            UserProfile: Схема профиля пользователя
        """
        return UserProfile(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            middle_name=user.middle_name,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
            roles=[role.name for role in user.roles] if user.roles else [],
            permissions=[]  # Без разрешений в базовом профиле
        )
    
    @staticmethod
    def user_to_profile_with_permissions(user: User) -> UserProfile:
        """
        Преобразовать пользователя в профиль с разрешениями
        
        Args:
            user: Модель пользователя с загруженными ролями и разрешениями
            
        Returns:
            UserProfile: Схема профиля пользователя с разрешениями
        """
        # Собираем все разрешения из всех ролей пользователя
        permissions = set()
        roles = []
        
        for role in user.roles if user.roles else []:
            roles.append(role.name)
            for permission in role.permissions if role.permissions else []:
                permissions.add(permission.name)
        
        return UserProfile(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            middle_name=user.middle_name,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
            roles=roles,
            permissions=list(permissions)
        )
