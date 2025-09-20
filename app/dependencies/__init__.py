"""
Модуль зависимостей приложения
Содержит все Dependency Injection функции
"""

# Основные зависимости из core_dependencies.py
from app.core_dependencies import (
    get_current_user,
    get_active_user,
    get_admin_user,
    require_permission,
    get_token_from_request
)

# Базовая зависимость базы данных
from app.database import get_db

# Админские зависимости
from .admin import (
    AdminPanelDependencyFactory,
    get_admin_panel_service,
    get_system_statistics_service,
    get_user_management_service,
    get_role_management_service,
    get_permission_service,
    get_user_repository,
    get_role_repository,
    get_permission_repository,
    get_resource_repository,
    get_system_mappers,
    get_system_validators
)

# Пользовательские зависимости
from .user import (
    UserProfileDependencyFactory,
    get_user_profile_service,
    get_user_auth_service
)

# Auth зависимости
from .auth import (
    AuthDependencyFactory,
    get_auth_service
)

# Resources зависимости
from .resources import (
    ResourcesDependencyFactory,
    get_resources_service
)

__all__ = [
    # Основные зависимости
    "get_db",
    "get_current_user",
    "get_active_user",
    "get_admin_user",
    "require_permission",
    "get_token_from_request",
    
    # Админские зависимости
    "AdminPanelDependencyFactory",
    "get_admin_panel_service",
    "get_system_statistics_service",
    "get_user_management_service",
    "get_role_management_service",
    "get_permission_service",
    "get_user_repository",
    "get_role_repository",
    "get_permission_repository",
    "get_resource_repository",
    "get_system_mappers",
    "get_system_validators",
    
    # Пользовательские зависимости
    "UserProfileDependencyFactory",
    "get_user_profile_service",
    "get_user_auth_service",
    
    # Auth зависимости
    "AuthDependencyFactory",
    "get_auth_service",
    
    # Resources зависимости
    "ResourcesDependencyFactory",
    "get_resources_service"
]
