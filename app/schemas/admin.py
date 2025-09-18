# app/schemas/admin.py
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr


class UserListItem(BaseModel):
    """Элемент списка пользователей для админ-панели"""
    id: int
    email: EmailStr
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    is_active: bool
    created_at: datetime
    roles: List[str] = []
    
    class Config:
        from_attributes = True


class UserRoleUpdate(BaseModel):
    """Схема для обновления ролей пользователя"""
    role_names: List[str]


class RoleResponse(BaseModel):
    """Схема ответа роли"""
    id: int
    name: str
    description: Optional[str] = None
    is_active: bool
    created_at: datetime
    permissions: List[str] = []
    
    class Config:
        from_attributes = True


class RoleCreate(BaseModel):
    """Схема создания роли"""
    name: str
    description: Optional[str] = None
    permission_names: List[str] = []


class PermissionResponse(BaseModel):
    """Схема ответа разрешения"""
    id: int
    name: str
    resource_type: str
    action: str
    description: Optional[str] = None
    
    class Config:
        from_attributes = True


class AdminStatsResponse(BaseModel):
    """Статистика для админ-панели"""
    total_users: int
    active_users: int
    inactive_users: int
    total_roles: int
    total_permissions: int
    total_resources: int
