"""
Сервис для сбора статистики системы
Агрегирует данные из всех репозиториев для админ-панели
"""

import asyncio
from typing import Dict

from ...repositories.user_repository import UserRepository
from ...repositories.role_repository import RoleRepository
from ...repositories.permission_repository import PermissionRepository
from ...repositories.resource_repository import ResourceRepository
from ...mappers.system_mappers import SystemMappers
from ...schemas.admin import AdminStatsResponse


from ..base_service import BaseService

class SystemStatisticsService(BaseService):
    """
    Сервис для сбора статистики системы
    Выполняет параллельные запросы к репозиториям для получения агрегированных данных
    """
    
    def __init__(
        self,
        user_repo: UserRepository,
        role_repo: RoleRepository,
        permission_repo: PermissionRepository,
        resource_repo: ResourceRepository
    ):
        super().__init__()
        self.user_repo = user_repo
        self.role_repo = role_repo
        self.permission_repo = permission_repo
        self.resource_repo = resource_repo
    
    async def get_system_stats(self) -> AdminStatsResponse:
        """
        Получить полную статистику системы
        
        Выполняет параллельные запросы для максимальной производительности
        
        Returns:
            AdminStatsResponse: Полная статистика системы
        """
        try:
            # Параллельно собираем все статистики
            user_stats_task = self.get_user_statistics()
            role_stats_task = self.get_role_statistics()
            permission_stats_task = self.get_permission_statistics()
            resource_stats_task = self.get_resource_statistics()
            
            # Ждем выполнения всех задач
            user_stats, role_stats, permission_stats, resource_stats = await asyncio.gather(
                user_stats_task,
                role_stats_task,
                permission_stats_task,
                resource_stats_task
            )
            
            # Создаем и возвращаем агрегированную статистику
            return SystemMappers.create_admin_stats_response(
                total_users=user_stats["total"],
                active_users=user_stats["active"],
                inactive_users=user_stats["inactive"],
                total_roles=role_stats["total"],
                total_permissions=permission_stats["total"],
                total_resources=resource_stats["total"]
            )
        except Exception as e:
            self._handle_service_error(e, "get_system_stats")
            raise
    
    async def get_user_statistics(self) -> Dict[str, int]:
        """
        Получить статистику пользователей
        
        Returns:
            Dict[str, int]: Статистика пользователей
        """
        try:
            # Параллельно получаем все счетчики пользователей
            total_task = self.user_repo.count()
            active_task = self.user_repo.get_active_users_count()
            inactive_task = self.user_repo.get_inactive_users_count()
            
            total, active, inactive = await asyncio.gather(
                total_task,
                active_task,
                inactive_task
            )
            
            return {
                "total": total,
                "active": active,
                "inactive": inactive,
                "percentage_active": round((active / total * 100) if total > 0 else 0, 2)
            }
        except Exception as e:
            self._handle_service_error(e, "get_user_statistics")
            raise
    
    async def get_role_statistics(self) -> Dict[str, int]:
        """
        Получить статистику ролей
        
        Returns:
            Dict[str, int]: Статистика ролей
        """
        try:
            # Параллельно получаем все счетчики ролей
            total_task = self.role_repo.count()
            active_task = self.role_repo.get_active_roles_count()
            inactive_task = self.role_repo.get_inactive_roles_count()
            
            total, active, inactive = await asyncio.gather(
                total_task,
                active_task,
                inactive_task
            )
            
            return {
                "total": total,
                "active": active,
                "inactive": inactive,
                "percentage_active": round((active / total * 100) if total > 0 else 0, 2)
            }
        except Exception as e:
            self._handle_service_error(e, "get_role_statistics")
            raise
    
    async def get_permission_statistics(self) -> Dict[str, int]:
        """
        Получить статистику разрешений
        
        Returns:
            Dict[str, int]: Статистика разрешений
        """
        try:
            # Параллельно получаем статистику разрешений
            total_task = self.permission_repo.count()
            resource_types_task = self.permission_repo.get_unique_resource_types()
            actions_task = self.permission_repo.get_unique_actions()
            by_resource_task = self.permission_repo.get_permissions_count_by_resource_type()
            
            total, resource_types, actions, by_resource = await asyncio.gather(
                total_task,
                resource_types_task,
                actions_task,
                by_resource_task
            )
            
            return {
                "total": total,
                "unique_resource_types": len(resource_types),
                "unique_actions": len(actions),
                "by_resource_type": {item["resource_type"]: item["count"] for item in by_resource}
            }
        except Exception as e:
            self._handle_service_error(e, "get_permission_statistics")
            raise
    
    async def get_resource_statistics(self) -> Dict[str, int]:
        """
        Получить статистику ресурсов
        
        Returns:
            Dict[str, int]: Статистика ресурсов
        """
        try:
            # Параллельно получаем все счетчики ресурсов
            total_task = self.resource_repo.count()
            active_task = self.resource_repo.get_active_resources_count()
            inactive_task = self.resource_repo.get_inactive_resources_count()
            types_task = self.resource_repo.get_unique_resource_types()
            by_type_task = self.resource_repo.get_resources_count_by_type()
            
            total, active, inactive, types, by_type = await asyncio.gather(
                total_task,
                active_task,
                inactive_task,
                types_task,
                by_type_task
            )
            
            return {
                "total": total,
                "active": active,
                "inactive": inactive,
                "unique_types": len(types),
                "by_type": {item["resource_type"]: item["count"] for item in by_type}
            }
        except Exception as e:
            self._handle_service_error(e, "get_resource_statistics")
            raise
    
    async def get_detailed_system_overview(self) -> Dict[str, any]:
        """
        Получить детальный обзор системы
        
        Returns:
            Dict[str, any]: Детальная статистика системы
        """
        try:
            # Параллельно собираем все детальные статистики
            user_stats_task = self.get_user_statistics()
            role_stats_task = self.get_role_statistics()
            permission_stats_task = self.get_permission_statistics()
            resource_stats_task = self.get_resource_statistics()
            
            user_stats, role_stats, permission_stats, resource_stats = await asyncio.gather(
                user_stats_task,
                role_stats_task,
                permission_stats_task,
                resource_stats_task
            )
            
            return {
                "users": user_stats,
                "roles": role_stats,
                "permissions": permission_stats,
                "resources": resource_stats,
                "system_health": {
                    "total_entities": (
                        user_stats["total"] + 
                        role_stats["total"] + 
                        permission_stats["total"] + 
                        resource_stats["total"]
                    ),
                    "active_entities": (
                        user_stats["active"] + 
                        role_stats["active"] + 
                        resource_stats["active"] + 
                        permission_stats["total"]  # Разрешения всегда активны
                    )
                }
            }
        except Exception as e:
            self._handle_service_error(e, "get_detailed_system_overview")
            raise
    
    async def get_quick_stats(self) -> Dict[str, int]:
        """
        Получить быструю статистику (только основные счетчики)
        
        Returns:
            Dict[str, int]: Основные счетчики системы
        """
        try:
            # Параллельно получаем только основные счетчики
            total_users_task = self.user_repo.count()
            total_roles_task = self.role_repo.count()
            total_permissions_task = self.permission_repo.count()
            total_resources_task = self.resource_repo.count()
            
            total_users, total_roles, total_permissions, total_resources = await asyncio.gather(
                total_users_task,
                total_roles_task,
                total_permissions_task,
                total_resources_task
            )
            
            return {
                "users": total_users,
                "roles": total_roles,
                "permissions": total_permissions,
                "resources": total_resources
            }
        except Exception as e:
            self._handle_service_error(e, "get_quick_stats")
            raise
