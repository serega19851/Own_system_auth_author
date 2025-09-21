# app/services/resources/permission_check_service.py

from typing import Set

from app.models import User
from app.schemas.resources import PermissionCheckResponse


from ..base_service import BaseService

class PermissionCheckService(BaseService):
    """Сервис для проверки разрешений пользователей"""
    
    async def check_user_permission(self, user: User, resource_type: str, action: str) -> PermissionCheckResponse:
        """Проверить разрешение пользователя на действие с ресурсом"""
        try:
            # Собираем все разрешения пользователя
            user_permissions = self._collect_user_permissions(user)
            
            # Формируем имя проверяемого разрешения
            permission_name = self._format_permission_name(resource_type, action)
            has_permission = permission_name in user_permissions
            
            message = f"User has {'✅' if has_permission else '❌'} permission '{permission_name}'"
            
            return PermissionCheckResponse(
                user_id=user.id,
                email=user.email,
                resource_type=resource_type,
                action=action,
                has_permission=has_permission,
                user_permissions=list(user_permissions),
                message=message
            )
        except Exception as e:
            self._handle_service_error(e, "check_user_permission")
            raise
    
    def _collect_user_permissions(self, user: User) -> Set[str]:
        """Собрать все разрешения пользователя"""
        user_permissions = set()
        for role in user.roles:
            for permission in role.permissions:
                user_permissions.add(permission.name)
        return user_permissions
    
    def _format_permission_name(self, resource_type: str, action: str) -> str:
        """Сформировать имя разрешения"""
        return f"{resource_type}_{action}"
