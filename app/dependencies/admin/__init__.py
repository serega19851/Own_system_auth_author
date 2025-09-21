"""
Модуль зависимостей для админ-панели
Содержит Dependency Injection Factory и функции для создания сервисов
"""

from .admin_panel_dependencies import (
    AdminPanelDependencyFactory,
    get_system_statistics_service,
    get_user_management_service,
    get_role_management_service,
    get_permission_service,
)

__all__ = [
    "AdminPanelDependencyFactory",
    "get_system_statistics_service",
    "get_user_management_service",
    "get_role_management_service",
    "get_permission_service",
]
