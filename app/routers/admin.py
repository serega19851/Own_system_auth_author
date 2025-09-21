# app/routers/admin.py
from typing import List
from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer

from app.dependencies import get_admin_user, get_admin_panel_service
from app.models import User
from app.services.admin import AdminPanelService
from app.schemas.admin import (
    UserListItem, UserRoleUpdate, RoleResponse, RoleCreate, 
    PermissionResponse, AdminStatsResponse
)

router = APIRouter(prefix="/admin", tags=["admin"])
security = HTTPBearer()


@router.get("/stats", response_model=AdminStatsResponse, dependencies=[Depends(security)])
async def get_admin_stats(
    admin_panel: AdminPanelService = Depends(get_admin_panel_service)
):
    """Получить статистику системы для админ-панели"""
    return await admin_panel.get_system_stats()


@router.get("/users", response_model=List[UserListItem], dependencies=[Depends(security)])
async def get_all_users(
    admin_panel: AdminPanelService = Depends(get_admin_panel_service)
):
    """Получить список всех пользователей"""
    return await admin_panel.get_all_users()


@router.put("/users/{user_id}/roles", response_model=UserListItem, dependencies=[Depends(security)])
async def update_user_roles(
    user_id: int,
    role_update: UserRoleUpdate,
    admin_panel: AdminPanelService = Depends(get_admin_panel_service),
):
    """Обновить роли пользователя"""
    return await admin_panel.update_user_roles(user_id, role_update)


@router.get("/roles", response_model=List[RoleResponse], dependencies=[Depends(security)])
async def get_all_roles(
    admin_panel: AdminPanelService = Depends(get_admin_panel_service)
):
    """Получить список всех ролей"""
    return await admin_panel.get_all_roles()


@router.post("/roles", response_model=RoleResponse, dependencies=[Depends(security)])
async def create_role(
    role_data: RoleCreate,
    admin_panel: AdminPanelService = Depends(get_admin_panel_service),
):
    """Создать новую роль"""
    return await admin_panel.create_role(role_data)


@router.get("/permissions", response_model=List[PermissionResponse], dependencies=[Depends(security)])
async def get_all_permissions(
    admin_panel: AdminPanelService = Depends(get_admin_panel_service)
):
    """Получить список всех разрешений"""
    return await admin_panel.get_all_permissions()
