"""
Фасад-координатор для админ-панели
Объединяет все специализированные сервисы в единую точку входа
"""

from typing import List

from .system_statistics_service import SystemStatisticsService
from .user_management_service import UserManagementService
from .role_management_service import RoleManagementService
from .permission_service import PermissionService
from ..base_service import BaseService

from ...schemas.admin import (
    AdminStatsResponse,
    UserListItem,
    UserRoleUpdate,
    RoleResponse,
    RoleCreate,
    PermissionResponse
)


class AdminPanelService(BaseService):
    """
    Фасад-координатор для админ-панели
    Предоставляет единый интерфейс для всех административных операций
    Делегирует вызовы специализированным сервисам
    """
    
    def __init__(
        self,
        statistics_service: SystemStatisticsService,
        user_management_service: UserManagementService,
        role_management_service: RoleManagementService,
        permission_service: PermissionService
    ):
        super().__init__()
        self.statistics_service = statistics_service
        self.user_management_service = user_management_service
        self.role_management_service = role_management_service
        self.permission_service = permission_service
    
    # ============================================================================
    # СТАТИСТИКА СИСТЕМЫ
    # ============================================================================
    
    async def get_system_stats(self) -> AdminStatsResponse:
        """
        Получить статистику системы для админ-панели
        
        Returns:
            AdminStatsResponse: Полная статистика системы
        """
        try:
            return await self.statistics_service.get_system_stats()
        except Exception as e:
            self._handle_service_error(e, "get_system_stats")
            raise
    
    async def get_detailed_system_overview(self) -> dict:
        """
        Получить детальный обзор системы
        
        Returns:
            dict: Детальная статистика всех компонентов системы
        """
        try:
            return await self.statistics_service.get_detailed_system_overview()
        except Exception as e:
            self._handle_service_error(e, "get_detailed_system_overview")
            raise
    
    async def get_quick_stats(self) -> dict:
        """
        Получить быструю статистику (основные счетчики)
        
        Returns:
            dict: Основные счетчики системы
        """
        try:
            return await self.statistics_service.get_quick_stats()
        except Exception as e:
            self._handle_service_error(e, "get_quick_stats")
            raise
    
    # ============================================================================
    # УПРАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯМИ
    # ============================================================================
    
    async def get_all_users(self) -> List[UserListItem]:
        """
        Получить всех пользователей с ролями
        
        Returns:
            List[UserListItem]: Список всех пользователей
        """
        try:
            return await self.user_management_service.get_all_users()
        except Exception as e:
            self._handle_service_error(e, "get_all_users")
            raise
    
    async def get_users_with_pagination(
        self, 
        page: int = 1, 
        size: int = 20
    ) -> List[UserListItem]:
        """
        Получить пользователей с пагинацией
        
        Args:
            page: Номер страницы
            size: Размер страницы
            
        Returns:
            List[UserListItem]: Список пользователей
        """
        try:
            return await self.user_management_service.get_users_with_pagination(page, size)
        except Exception as e:
            self._handle_service_error(e, "get_users_with_pagination")
            raise
    
    async def filter_users(
        self, 
        is_active: bool = None, 
        role_name: str = None
    ) -> List[UserListItem]:
        """
        Получить пользователей с фильтрацией
        
        Args:
            is_active: Фильтр по активности
            role_name: Фильтр по роли
            
        Returns:
            List[UserListItem]: Отфильтрованные пользователи
        """
        try:
            return await self.user_management_service.filter_users(is_active, role_name)
        except Exception as e:
            self._handle_service_error(e, "filter_users")
            raise
    
    async def update_user_roles(
        self, 
        user_id: int, 
        role_update: UserRoleUpdate
    ) -> UserListItem:
        """
        Обновить роли пользователя
        
        Args:
            user_id: ID пользователя
            role_update: Новые роли пользователя
            
        Returns:
            UserListItem: Обновленные данные пользователя
        """
        try:
            return await self.user_management_service.update_user_roles(user_id, role_update)
        except Exception as e:
            self._handle_service_error(e, "update_user_roles")
            raise
    
    async def search_users(self, search_term: str, limit: int = 20) -> List[UserListItem]:
        """
        Поиск пользователей
        
        Args:
            search_term: Поисковый запрос
            limit: Максимальное количество результатов
            
        Returns:
            List[UserListItem]: Найденные пользователи
        """
        try:
            return await self.user_management_service.search_users(search_term, limit)
        except Exception as e:
            self._handle_service_error(e, "search_users")
            raise
    
    async def get_user_details(self, user_id: int) -> UserListItem:
        """
        Получить детальную информацию о пользователе
        
        Args:
            user_id: ID пользователя
            
        Returns:
            UserListItem: Детальная информация о пользователе
        """
        try:
            return await self.user_management_service.get_user_details(user_id)
        except Exception as e:
            self._handle_service_error(e, "get_user_details")
            raise
    
    async def get_users_by_role(self, role_name: str) -> List[UserListItem]:
        """
        Получить пользователей с определенной ролью
        
        Args:
            role_name: Название роли
            
        Returns:
            List[UserListItem]: Пользователи с указанной ролью
        """
        try:
            return await self.user_management_service.get_users_by_role(role_name)
        except Exception as e:
            self._handle_service_error(e, "get_users_by_role")
            raise
    
    # ============================================================================
    # УПРАВЛЕНИЕ РОЛЯМИ
    # ============================================================================
    
    async def get_all_roles(self) -> List[RoleResponse]:
        """
        Получить все роли с разрешениями
        
        Returns:
            List[RoleResponse]: Список всех ролей
        """
        try:
            return await self.role_management_service.get_all_roles()
        except Exception as e:
            self._handle_service_error(e, "get_all_roles")
            raise
    
    async def get_roles_with_pagination(
        self, 
        page: int = 1, 
        size: int = 20
    ) -> List[RoleResponse]:
        """
        Получить роли с пагинацией
        
        Args:
            page: Номер страницы
            size: Размер страницы
            
        Returns:
            List[RoleResponse]: Список ролей
        """
        try:
            return await self.role_management_service.get_roles_with_pagination(page, size)
        except Exception as e:
            self._handle_service_error(e, "get_roles_with_pagination")
            raise
    
    async def create_role(self, role_data: RoleCreate) -> RoleResponse:
        """
        Создать новую роль
        
        Args:
            role_data: Данные для создания роли
            
        Returns:
            RoleResponse: Созданная роль
        """
        try:
            return await self.role_management_service.create_role(role_data)
        except Exception as e:
            self._handle_service_error(e, "create_role")
            raise
    
    async def get_role_details(self, role_id: int) -> RoleResponse:
        """
        Получить детальную информацию о роли
        
        Args:
            role_id: ID роли
            
        Returns:
            RoleResponse: Детальная информация о роли
        """
        try:
            return await self.role_management_service.get_role_details(role_id)
        except Exception as e:
            self._handle_service_error(e, "get_role_details")
            raise
    
    async def get_role_by_name(self, role_name: str) -> RoleResponse:
        """
        Получить роль по названию
        
        Args:
            role_name: Название роли
            
        Returns:
            RoleResponse: Информация о роли
        """
        try:
            return await self.role_management_service.get_role_by_name(role_name)
        except Exception as e:
            self._handle_service_error(e, "get_role_by_name")
            raise
    
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
        """
        try:
            return await self.role_management_service.assign_permissions_to_role(
                role_id, permission_names
            )
        except Exception as e:
            self._handle_service_error(e, "assign_permissions_to_role")
            raise
    
    async def add_permissions_to_role(
        self, 
        role_id: int, 
        permission_names: List[str]
    ) -> RoleResponse:
        """
        Добавить разрешения к роли
        
        Args:
            role_id: ID роли
            permission_names: Список названий разрешений для добавления
            
        Returns:
            RoleResponse: Роль с обновленными разрешениями
        """
        try:
            return await self.role_management_service.add_permissions_to_role(
                role_id, permission_names
            )
        except Exception as e:
            self._handle_service_error(e, "add_permissions_to_role")
            raise
    
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
        try:
            return await self.role_management_service.remove_permissions_from_role(
                role_id, permission_names
            )
        except Exception as e:
            self._handle_service_error(e, "remove_permissions_from_role")
            raise
    
    # ============================================================================
    # УПРАВЛЕНИЕ РАЗРЕШЕНИЯМИ
    # ============================================================================
    
    async def get_all_permissions(self) -> List[PermissionResponse]:
        """
        Получить все разрешения
        
        Returns:
            List[PermissionResponse]: Список всех разрешений
        """
        try:
            return await self.permission_service.get_all_permissions()
        except Exception as e:
            self._handle_service_error(e, "get_all_permissions")
            raise
    
    async def get_permissions_by_resource_type(self, resource_type: str) -> List[PermissionResponse]:
        """
        Получить разрешения по типу ресурса
        
        Args:
            resource_type: Тип ресурса
            
        Returns:
            List[PermissionResponse]: Разрешения для указанного типа ресурса
        """
        try:
            return await self.permission_service.get_permissions_by_resource_type(resource_type)
        except Exception as e:
            self._handle_service_error(e, "get_permissions_by_resource_type")
            raise
    
    async def get_permissions_with_pagination(
        self, 
        page: int = 1, 
        size: int = 20
    ) -> List[PermissionResponse]:
        """
        Получить разрешения с пагинацией
        
        Args:
            page: Номер страницы
            size: Размер страницы
            
        Returns:
            List[PermissionResponse]: Список разрешений с пагинацией
        """
        try:
            return await self.permission_service.get_permissions_with_pagination(page, size)
        except Exception as e:
            self._handle_service_error(e, "get_permissions_with_pagination")
            raise
    
    async def search_permissions(self, search_term: str) -> List[PermissionResponse]:
        """
        Поиск разрешений
        
        Args:
            search_term: Поисковый запрос
            
        Returns:
            List[PermissionResponse]: Найденные разрешения
        """
        try:
            return await self.permission_service.search_permissions(search_term)
        except Exception as e:
            self._handle_service_error(e, "search_permissions")
            raise
    
    async def get_permissions_grouped_by_resource_type(self) -> dict:
        """
        Получить разрешения, сгруппированные по типу ресурса
        
        Returns:
            dict: Разрешения, сгруппированные по типу ресурса
        """
        try:
            return await self.permission_service.get_permissions_grouped_by_resource_type()
        except Exception as e:
            self._handle_service_error(e, "get_permissions_grouped_by_resource_type")
            raise
    
    async def get_permissions_overview(self) -> dict:
        """
        Получить обзор разрешений
        
        Returns:
            dict: Обзор разрешений с группировкой и статистикой
        """
        try:
            return await self.permission_service.get_permissions_overview()
        except Exception as e:
            self._handle_service_error(e, "get_permissions_overview")
            raise
    
    # ============================================================================
    # КОМПЛЕКСНЫЕ ОПЕРАЦИИ
    # ============================================================================
    
    async def get_admin_dashboard_data(self) -> dict:
        """
        Получить все данные для админ-панели (дашборд)
        
        Returns:
            dict: Полные данные для админ-панели
        """
        try:
            import asyncio
            
            # Параллельно получаем все основные данные
            stats_task = self.get_system_stats()
            users_task = self.get_all_users()
            roles_task = self.get_all_roles()
            permissions_overview_task = self.get_permissions_overview()
            
            stats, users, roles, permissions_overview = await asyncio.gather(
                stats_task,
                users_task,
                roles_task,
                permissions_overview_task
            )
            
            return {
                "statistics": stats,
                "users": users[:10],  # Первые 10 пользователей для дашборда
                "roles": roles,
                "permissions_overview": permissions_overview,
                "summary": {
                    "total_users": len(users),
                    "total_roles": len(roles),
                    "total_permissions": permissions_overview["statistics"]["total"]
                }
            }
        except Exception as e:
            self._handle_service_error(e, "get_admin_dashboard_data")
            raise
    
    async def get_system_health_check(self) -> dict:
        """
        Проверить здоровье системы
        
        Returns:
            dict: Информация о состоянии системы
        """
        try:
            detailed_overview = await self.get_detailed_system_overview()
            
            system_health = detailed_overview.get("system_health", {})
            total_entities = system_health.get("total_entities", 0)
            active_entities = system_health.get("active_entities", 0)
            
            health_percentage = (active_entities / total_entities * 100) if total_entities > 0 else 0
            
            return {
                "status": "healthy" if health_percentage > 80 else "warning" if health_percentage > 50 else "critical",
                "health_percentage": round(health_percentage, 2),
                "total_entities": total_entities,
                "active_entities": active_entities,
                "detailed_stats": detailed_overview
            }
        except Exception as e:
            self._handle_service_error(e, "get_system_health_check")
            raise
