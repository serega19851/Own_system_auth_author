# app/routers/admin.py
from typing import List
from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer

from app.dependencies.admin.admin_panel_dependencies import (
    get_system_statistics_service,
    get_user_management_service,
    get_role_management_service,
    get_permission_service
)
from app.core_dependencies import require_permission
from app.services.admin.system_statistics_service import SystemStatisticsService
from app.services.admin.user_management_service import UserManagementService
from app.services.admin.role_management_service import RoleManagementService
from app.services.admin.permission_service import PermissionService
from app.schemas.admin import (
    UserListItem, UserRoleUpdate, RoleResponse, RoleCreate, 
    PermissionResponse, AdminStatsResponse
)
from app.models import User

router = APIRouter(prefix="/admin", tags=["admin"])
security = HTTPBearer()


@router.get("/stats", response_model=AdminStatsResponse)
async def get_admin_stats(
    current_user: User = Depends(require_permission("admin_system_config")),
    statistics_service: SystemStatisticsService = Depends(get_system_statistics_service)
):
    """Получить статистику системы для админ-панели - ТРЕБУЕТ РАЗРЕШЕНИЕ admin_system_config"""
    return await statistics_service.get_system_stats()


@router.get("/users", response_model=List[UserListItem])
async def get_all_users(
    current_user: User = Depends(require_permission("admin_users_manage")),
    user_management_service: UserManagementService = Depends(get_user_management_service)
):
    """Получить список всех пользователей - ТРЕБУЕТ РАЗРЕШЕНИЕ admin_users_manage"""
    return await user_management_service.get_all_users()


@router.put("/users/{user_id}/roles", response_model=UserListItem)
async def update_user_roles(
    user_id: int,
    role_update: UserRoleUpdate,
    current_user: User = Depends(require_permission("admin_users_manage")),
    user_management_service: UserManagementService = Depends(get_user_management_service),
):
    """Обновить роли пользователя - ТРЕБУЕТ РАЗРЕШЕНИЕ admin_users_manage"""
    return await user_management_service.update_user_roles(user_id, role_update)


@router.get("/roles", response_model=List[RoleResponse])
async def get_all_roles(
    current_user: User = Depends(require_permission("admin_roles_manage")),
    role_management_service: RoleManagementService = Depends(get_role_management_service)
):
    """Получить список всех ролей - ТРЕБУЕТ РАЗРЕШЕНИЕ admin_roles_manage"""
    return await role_management_service.get_all_roles()


@router.post("/roles", response_model=RoleResponse)
async def create_role(
    role_data: RoleCreate,
    current_user: User = Depends(require_permission("admin_roles_manage")),
    role_management_service: RoleManagementService = Depends(get_role_management_service),
):
    """Создать новую роль - ТРЕБУЕТ РАЗРЕШЕНИЕ admin_roles_manage"""
    return await role_management_service.create_role(role_data)


@router.get("/permissions", response_model=List[PermissionResponse])
async def get_all_permissions(
    current_user: User = Depends(require_permission("admin_roles_manage")),
    permission_service: PermissionService = Depends(get_permission_service)
):
    """Получить список всех разрешений - ТРЕБУЕТ РАЗРЕШЕНИЕ admin_roles_manage"""
    return await permission_service.get_all_permissions()
