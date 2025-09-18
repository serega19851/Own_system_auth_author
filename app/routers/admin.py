# app/routers/admin.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, text
from sqlalchemy.orm import selectinload

from app.dependencies import get_db, get_admin_user
from app.models import User, Role, Permission, Resource
from app.schemas.admin import (
    UserListItem, UserRoleUpdate, RoleResponse, RoleCreate, 
    PermissionResponse, AdminStatsResponse
)

router = APIRouter(prefix="/admin", tags=["admin"])
security = HTTPBearer()


@router.get("/stats", response_model=AdminStatsResponse, dependencies=[Depends(security)])
async def get_admin_stats(
    admin_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Получить статистику системы для админ-панели"""
    
    # Подсчет пользователей
    total_users = await db.scalar(select(func.count(User.id)))
    active_users = await db.scalar(select(func.count(User.id)).where(User.is_active == True))
    inactive_users = total_users - active_users
    
    # Подсчет ролей, разрешений и ресурсов
    total_roles = await db.scalar(select(func.count(Role.id)))
    total_permissions = await db.scalar(select(func.count(Permission.id)))
    total_resources = await db.scalar(select(func.count(Resource.id)))
    
    return AdminStatsResponse(
        total_users=total_users,
        active_users=active_users,
        inactive_users=inactive_users,
        total_roles=total_roles,
        total_permissions=total_permissions,
        total_resources=total_resources
    )


@router.get("/users", response_model=List[UserListItem], dependencies=[Depends(security)])
async def get_all_users(
    admin_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Получить список всех пользователей"""
    
    stmt = select(User).options(selectinload(User.roles)).order_by(User.id)
    result = await db.execute(stmt)
    users = result.scalars().all()
    
    # Формируем ответ
    users_list = []
    for user in users:
        roles = [role.name for role in user.roles]
        users_list.append(UserListItem(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            middle_name=user.middle_name,
            is_active=user.is_active,
            created_at=user.created_at,
            roles=roles
        ))
    
    return users_list


@router.put("/users/{user_id}/roles", response_model=UserListItem, dependencies=[Depends(security)])
async def update_user_roles(
    user_id: int,
    role_update: UserRoleUpdate,
    admin_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Обновить роли пользователя"""
    
    # Проверяем, что пользователь существует
    user_stmt = select(User).options(selectinload(User.roles)).where(User.id == user_id)
    result = await db.execute(user_stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Получаем роли по именам
    roles_stmt = select(Role).where(Role.name.in_(role_update.role_names))
    roles_result = await db.execute(roles_stmt)
    new_roles = roles_result.scalars().all()
    
    # Проверяем, что все роли существуют
    found_role_names = {role.name for role in new_roles}
    missing_roles = set(role_update.role_names) - found_role_names
    if missing_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Roles not found: {', '.join(missing_roles)}"
        )
    
    # Удаляем старые связи пользователь-роль
    await db.execute(
        text("DELETE FROM user_roles WHERE user_id = :user_id"),
        {"user_id": user_id}
    )
    
    # Добавляем новые связи
    for role in new_roles:
        await db.execute(
            text("INSERT INTO user_roles (user_id, role_id) VALUES (:user_id, :role_id)"),
            {"user_id": user_id, "role_id": role.id}
        )
    
    await db.commit()
    
    # Возвращаем обновленного пользователя
    updated_user_stmt = select(User).options(selectinload(User.roles)).where(User.id == user_id)
    updated_result = await db.execute(updated_user_stmt)
    updated_user = updated_result.scalar_one()
    
    roles = [role.name for role in updated_user.roles]
    return UserListItem(
        id=updated_user.id,
        email=updated_user.email,
        first_name=updated_user.first_name,
        last_name=updated_user.last_name,
        middle_name=updated_user.middle_name,
        is_active=updated_user.is_active,
        created_at=updated_user.created_at,
        roles=roles
    )


@router.get("/roles", response_model=List[RoleResponse], dependencies=[Depends(security)])
async def get_all_roles(
    admin_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Получить список всех ролей"""
    
    stmt = select(Role).options(selectinload(Role.permissions)).order_by(Role.id)
    result = await db.execute(stmt)
    roles = result.scalars().all()
    
    # Формируем ответ
    roles_list = []
    for role in roles:
        permissions = [perm.name for perm in role.permissions]
        roles_list.append(RoleResponse(
            id=role.id,
            name=role.name,
            description=role.description,
            is_active=role.is_active,
            created_at=role.created_at,
            permissions=permissions
        ))
    
    return roles_list


@router.post("/roles", response_model=RoleResponse, dependencies=[Depends(security)])
async def create_role(
    role_data: RoleCreate,
    admin_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Создать новую роль"""
    
    # Проверяем, что роль с таким именем не существует
    existing_role = await db.scalar(select(Role).where(Role.name == role_data.name))
    if existing_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Role '{role_data.name}' already exists"
        )
    
    # Создаем роль
    new_role = Role(
        name=role_data.name,
        description=role_data.description,
        is_active=True
    )
    db.add(new_role)
    await db.flush()  # Получаем ID
    
    # Добавляем разрешения, если указаны
    if role_data.permission_names:
        permissions_stmt = select(Permission).where(Permission.name.in_(role_data.permission_names))
        permissions_result = await db.execute(permissions_stmt)
        permissions = permissions_result.scalars().all()
        
        # Проверяем, что все разрешения существуют
        found_perm_names = {perm.name for perm in permissions}
        missing_perms = set(role_data.permission_names) - found_perm_names
        if missing_perms:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Permissions not found: {', '.join(missing_perms)}"
            )
        
        # Связываем роль с разрешениями
        for permission in permissions:
            await db.execute(
                text("INSERT INTO role_permissions (role_id, permission_id) VALUES (:role_id, :perm_id)"),
                {"role_id": new_role.id, "perm_id": permission.id}
            )
    
    await db.commit()
    
    # Возвращаем созданную роль
    created_role_stmt = select(Role).options(selectinload(Role.permissions)).where(Role.id == new_role.id)
    created_result = await db.execute(created_role_stmt)
    created_role = created_result.scalar_one()
    
    permissions = [perm.name for perm in created_role.permissions]
    return RoleResponse(
        id=created_role.id,
        name=created_role.name,
        description=created_role.description,
        is_active=created_role.is_active,
        created_at=created_role.created_at,
        permissions=permissions
    )


@router.get("/permissions", response_model=List[PermissionResponse], dependencies=[Depends(security)])
async def get_all_permissions(
    admin_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Получить список всех разрешений"""
    
    stmt = select(Permission).order_by(Permission.resource_type, Permission.action)
    result = await db.execute(stmt)
    permissions = result.scalars().all()
    
    return [
        PermissionResponse(
            id=perm.id,
            name=perm.name,
            resource_type=perm.resource_type,
            action=perm.action,
            description=perm.description
        )
        for perm in permissions
    ]
