"""
Модуль репозиториев для работы с данными
Содержит базовый репозиторий и специализированные репозитории для каждой модели
"""

from .base_repository import BaseRepository
from .user_repository import UserRepository
from .role_repository import RoleRepository
from .permission_repository import PermissionRepository
from .resource_repository import ResourceRepository

__all__ = [
    "BaseRepository",
    "UserRepository", 
    "RoleRepository",
    "PermissionRepository",
    "ResourceRepository"
]
