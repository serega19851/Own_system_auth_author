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
from app.services.admin.system_statistics_service import SystemStatisticsService
from app.services.admin.user_management_service import UserManagementService
from app.services.admin.role_management_service import RoleManagementService
from app.services.admin.permission_service import PermissionService
from app.schemas.admin import (
    UserListItem, UserRoleUpdate, RoleResponse, RoleCreate, 
    PermissionResponse, AdminStatsResponse
)

router = APIRouter(prefix="/admin", tags=["admin"])
security = HTTPBearer()


@router.get("/stats", response_model=AdminStatsResponse, dependencies=[Depends(security)])
async def get_admin_stats(
    statistics_service: SystemStatisticsService = Depends(get_system_statistics_service)
):
    """Получить статистику системы для админ-панели"""
    return await statistics_service.get_system_stats()


@router.get("/users", response_model=List[UserListItem], dependencies=[Depends(security)])
async def get_all_users(
    user_management_service: UserManagementService = Depends(get_user_management_service)
):
    """Получить список всех пользователей"""
    return await user_management_service.get_all_users()


@router.put("/users/{user_id}/roles", response_model=UserListItem, dependencies=[Depends(security)])
async def update_user_roles(
    user_id: int,
    role_update: UserRoleUpdate,
    user_management_service: UserManagementService = Depends(get_user_management_service),
):
    """Обновить роли пользователя"""
    return await user_management_service.update_user_roles(user_id, role_update)


@router.get("/roles", response_model=List[RoleResponse], dependencies=[Depends(security)])
async def get_all_roles(
    role_management_service: RoleManagementService = Depends(get_role_management_service)
):
    """Получить список всех ролей"""
    return await role_management_service.get_all_roles()


@router.post("/roles", response_model=RoleResponse, dependencies=[Depends(security)])
async def create_role(
    role_data: RoleCreate,
    role_management_service: RoleManagementService = Depends(get_role_management_service),
):
    """Создать новую роль"""
    return await role_management_service.create_role(role_data)


@router.get("/permissions", response_model=List[PermissionResponse], dependencies=[Depends(security)])
async def get_all_permissions(
    permission_service: PermissionService = Depends(get_permission_service)
):
    """Получить список всех разрешений"""
    return await permission_service.get_all_permissions()
