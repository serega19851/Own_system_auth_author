"""
Модуль зависимостей для админ-панели
Содержит Dependency Injection Factory и функции для создания сервисов
"""

from .admin_panel_dependencies import (
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

__all__ = [
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
    "get_system_validators"
]
