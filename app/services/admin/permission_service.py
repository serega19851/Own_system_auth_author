"""
Сервис для управления разрешениями в админ-панели
Инкапсулирует логику работы с разрешениями для административных операций
"""

from typing import List, Optional, Dict

from ...repositories.permission_repository import PermissionRepository
from ...mappers.system_mappers import SystemMappers
from ...schemas.admin import PermissionResponse


from ..base_service import BaseService

class PermissionService(BaseService):
    """
    Сервис для управления разрешениями в контексте админ-панели
    Содержит всю бизнес-логику для операций с разрешениями
    """
    
    def __init__(
        self,
        permission_repo: PermissionRepository,
        mappers: SystemMappers
    ):
        super().__init__()
        self.permission_repo = permission_repo
        self.mappers = mappers
    
    async def get_all_permissions(self) -> List[PermissionResponse]:
        """
        Получить все разрешения для админ-панели
        
        Returns:
            List[PermissionResponse]: Список всех разрешений
        """
        try:
            # Получаем все разрешения, отсортированные по типу ресурса
            permissions = await self.permission_repo.get_ordered_by_resource_type()
            
            # Преобразуем в схемы ответа
            return self.mappers.permissions_to_responses(permissions)
        except Exception as e:
            self._handle_service_error(e, "get_all_permissions")
            raise
    
    async def get_permissions_by_resource_type(self, resource_type: str) -> List[PermissionResponse]:
        """
        Получить разрешения по типу ресурса
        
        Args:
            resource_type: Тип ресурса (documents, reports, etc.)
            
        Returns:
            List[PermissionResponse]: Список разрешений для указанного типа ресурса
        """
        try:
            permissions = await self.permission_repo.get_by_resource_type(resource_type)
            return self.mappers.permissions_to_responses(permissions)
        except Exception as e:
            self._handle_service_error(e, "get_permissions_by_resource_type")
            raise
    
    async def get_permissions_by_action(self, action: str) -> List[PermissionResponse]:
        """
        Получить разрешения по действию
        
        Args:
            action: Действие (read, write, create, delete, etc.)
            
        Returns:
            List[PermissionResponse]: Список разрешений для указанного действия
        """
        try:
            permissions = await self.permission_repo.get_by_action(action)
            return self.mappers.permissions_to_responses(permissions)
        except Exception as e:
            self._handle_service_error(e, "get_permissions_by_action")
            raise
    
    async def get_permissions_with_pagination(
        self, 
        page: int = 1, 
        size: int = 50
    ) -> List[PermissionResponse]:
        """
        Получить разрешения с пагинацией
        
        Args:
            page: Номер страницы (начиная с 1)
            size: Размер страницы
            
        Returns:
            List[PermissionResponse]: Список разрешений
        """
        try:
            offset = (page - 1) * size
            
            # Получаем разрешения с пагинацией
            permissions = await self.permission_repo.get_with_limit(
                limit=size, 
                offset=offset
            )
            
            return self.mappers.permissions_to_responses(permissions)
        except Exception as e:
            self._handle_service_error(e, "get_permissions_with_pagination")
            raise
    
    async def search_permissions(self, search_term: str) -> List[PermissionResponse]:
        """
        Поиск разрешений по названию, типу ресурса или действию
        
        Args:
            search_term: Поисковый запрос
            
        Returns:
            List[PermissionResponse]: Найденные разрешения
        """
        try:
            permissions = await self.permission_repo.search_permissions(search_term)
            return self.mappers.permissions_to_responses(permissions)
        except Exception as e:
            self._handle_service_error(e, "search_permissions")
            raise
    
    async def get_permission_by_name(self, permission_name: str) -> Optional[PermissionResponse]:
        """
        Получить разрешение по названию
        
        Args:
            permission_name: Название разрешения
            
        Returns:
            Optional[PermissionResponse]: Разрешение или None
        """
        try:
            permission = await self.permission_repo.get_by_name(permission_name)
            
            if permission:
                return self.mappers.permission_to_response(permission)
            
            return None
        except Exception as e:
            self._handle_service_error(e, "get_permission_by_name")
            raise
    
    async def get_permission_by_resource_and_action(
        self, 
        resource_type: str, 
        action: str
    ) -> Optional[PermissionResponse]:
        """
        Получить разрешение по типу ресурса и действию
        
        Args:
            resource_type: Тип ресурса
            action: Действие
            
        Returns:
            Optional[PermissionResponse]: Разрешение или None
        """
        try:
            permission = await self.permission_repo.get_by_resource_and_action(
                resource_type, action
            )
            
            if permission:
                return self.mappers.permission_to_response(permission)
            
            return None
        except Exception as e:
            self._handle_service_error(e, "get_permission_by_resource_and_action")
            raise
    
    async def get_unique_resource_types(self) -> List[str]:
        """
        Получить список уникальных типов ресурсов
        
        Returns:
            List[str]: Список уникальных типов ресурсов
        """
        try:
            return await self.permission_repo.get_unique_resource_types()
        except Exception as e:
            self._handle_service_error(e, "get_unique_resource_types")
            raise
    
    async def get_unique_actions(self) -> List[str]:
        """
        Получить список уникальных действий
        
        Returns:
            List[str]: Список уникальных действий
        """
        try:
            return await self.permission_repo.get_unique_actions()
        except Exception as e:
            self._handle_service_error(e, "get_unique_actions")
            raise
    
    async def get_permissions_grouped_by_resource_type(self) -> Dict[str, List[PermissionResponse]]:
        """
        Получить разрешения, сгруппированные по типу ресурса
        
        Returns:
            Dict[str, List[PermissionResponse]]: Разрешения, сгруппированные по типу ресурса
        """
        try:
            all_permissions = await self.permission_repo.get_ordered_by_resource_type()
            
            # Группируем разрешения по типу ресурса
            grouped_permissions = {}
            for permission in all_permissions:
                resource_type = permission.resource_type
                
                if resource_type not in grouped_permissions:
                    grouped_permissions[resource_type] = []
                
                grouped_permissions[resource_type].append(
                    self.mappers.permission_to_response(permission)
                )
            
            return grouped_permissions
        except Exception as e:
            self._handle_service_error(e, "get_permissions_grouped_by_resource_type")
            raise
    
    async def get_permissions_statistics(self) -> Dict[str, any]:
        """
        Получить статистику разрешений
        
        Returns:
            Dict[str, any]: Статистика разрешений
        """
        try:
            total_permissions = await self.permission_repo.count()
            unique_resource_types = await self.permission_repo.get_unique_resource_types()
            unique_actions = await self.permission_repo.get_unique_actions()
            permissions_by_resource = await self.permission_repo.get_permissions_count_by_resource_type()
            
            return {
                "total": total_permissions,
                "unique_resource_types": len(unique_resource_types),
                "unique_actions": len(unique_actions),
                "resource_types": unique_resource_types,
                "actions": unique_actions,
                "by_resource_type": {
                    item["resource_type"]: item["count"] 
                    for item in permissions_by_resource
                }
            }
        except Exception as e:
            self._handle_service_error(e, "get_permissions_statistics")
            raise
    
    async def get_permissions_overview(self) -> Dict[str, any]:
        """
        Получить обзор разрешений для админ-панели
        
        Returns:
            Dict[str, any]: Обзор разрешений с группировкой и статистикой
        """
        try:
            # Параллельно получаем статистику и группировку
            import asyncio
            
            stats_task = self.get_permissions_statistics()
            grouped_task = self.get_permissions_grouped_by_resource_type()
            
            stats, grouped = await asyncio.gather(stats_task, grouped_task)
            
            return {
                "statistics": stats,
                "grouped_by_resource": grouped,
                "total_groups": len(grouped)
            }
        except Exception as e:
            self._handle_service_error(e, "get_permissions_overview")
            raise
    
    async def check_permission_exists(self, resource_type: str, action: str) -> bool:
        """
        Проверить существование разрешения
        
        Args:
            resource_type: Тип ресурса
            action: Действие
            
        Returns:
            bool: True если разрешение существует
        """
        try:
            return await self.permission_repo.check_permission_exists(resource_type, action)
        except Exception as e:
            self._handle_service_error(e, "check_permission_exists")
            raise
    
    async def get_permissions_for_resource_types(
        self, 
        resource_types: List[str]
    ) -> Dict[str, List[PermissionResponse]]:
        """
        Получить разрешения для списка типов ресурсов
        
        Args:
            resource_types: Список типов ресурсов
            
        Returns:
            Dict[str, List[PermissionResponse]]: Разрешения для каждого типа ресурса
        """
        try:
            result = {}
            
            for resource_type in resource_types:
                permissions = await self.permission_repo.get_by_resource_type(resource_type)
                result[resource_type] = self.mappers.permissions_to_responses(permissions)
            
            return result
        except Exception as e:
            self._handle_service_error(e, "get_permissions_for_resource_types")
            raise
