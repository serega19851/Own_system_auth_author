"""
Модуль админских сервисов
Содержит специализированные сервисы для административных операций
"""

from .system_statistics_service import SystemStatisticsService
from .user_management_service import UserManagementService
from .role_management_service import RoleManagementService
from .permission_service import PermissionService
from .admin_panel_service import AdminPanelService

__all__ = [
    "SystemStatisticsService",
    "UserManagementService",
    "RoleManagementService",
    "PermissionService",
    "AdminPanelService"
]
