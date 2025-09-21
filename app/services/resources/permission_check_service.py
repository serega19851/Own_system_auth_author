# app/services/resources/permission_check_service.py

from typing import Set
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.schemas.resources import PermissionCheckResponse
from app.repositories.user_repository import UserRepository


from ..base_service import BaseService

class PermissionCheckService(BaseService):
    """Сервис для проверки разрешений пользователей"""
    
    def __init__(self, db: AsyncSession):
        super().__init__()
        self.user_repository = UserRepository(db)
    
    async def check_user_permission(self, user: User, resource_type: str, action: str) -> PermissionCheckResponse:
        """Проверить разрешение пользователя на действие с ресурсом"""
        try:
            # Получаем пользователя с ролями и разрешениями через репозиторий
            user_with_permissions = await self.user_repository.get_user_with_roles_and_permissions(user.id)
            
            if not user_with_permissions:
                return PermissionCheckResponse(
                    user_id=user.id,
                    email=user.email,
                    resource_type=resource_type,
                    action=action,
                    has_permission=False,
                    user_permissions=[],
                    message="Пользователь не найден"
                )
            
            # Собираем все разрешения пользователя через репозиторий
            user_permissions = self._collect_user_permissions(user_with_permissions)
            
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
        """
        Собрать все разрешения пользователя из активных ролей
        Данные получены через репозиторий с предзагруженными связями
        """
        user_permissions = set()
        for role in user.roles:
            if role.is_active:  # Учитываем только активные роли
                for permission in role.permissions:
                    user_permissions.add(permission.name)
        return user_permissions
    
    def _format_permission_name(self, resource_type: str, action: str) -> str:
        """Сформировать имя разрешения"""
        return f"{resource_type}_{action}"
