"""
Модуль сервисов
Содержит все бизнес-сервисы приложения
"""

# Пользовательские сервисы
from .user import UserProfileService

# Новые админские сервисы
from .admin import (
    SystemStatisticsService,
    UserManagementService,
    RoleManagementService,
    PermissionService,
)

__all__ = [
    # Пользовательские сервисы
    "UserProfileService",
    
    # Админские сервисы
    "SystemStatisticsService",
    "UserManagementService", 
    "RoleManagementService",
    "PermissionService",
]
