# app/routers/users.py
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from app.dependencies import get_db, get_active_user
from app.models import User, Permission, Role
from app.schemas.user import UserProfile, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])
security = HTTPBearer()


@router.get("/me", response_model=UserProfile, dependencies=[Depends(security)])
async def get_current_user_profile(
    current_user: User = Depends(get_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить профиль текущего пользователя
    Возвращает информацию о пользователе, его ролях и разрешениях
    """
    # Загружаем роли с разрешениями
    stmt = select(User).options(
        selectinload(User.roles).selectinload(Role.permissions)
    ).where(User.id == current_user.id)
    
    result = await db.execute(stmt)
    user = result.scalar_one()
    
    # Собираем все разрешения пользователя из всех его ролей
    permissions = set()
    roles = []
    
    for role in user.roles:
        roles.append(role.name)
        for permission in role.permissions:
            permissions.add(permission.name)
    
    # Формируем ответ
    user_profile = UserProfile(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        middle_name=user.middle_name,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at,
        roles=roles,
        permissions=list(permissions)
    )
    
    return user_profile


@router.put("/me", response_model=UserProfile, dependencies=[Depends(security)])
async def update_current_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Обновить профиль текущего пользователя
    Позволяет изменить имя, фамилию и отчество
    """
    # Подготавливаем данные для обновления
    update_data = {}
    if user_update.first_name is not None:
        update_data["first_name"] = user_update.first_name
    if user_update.last_name is not None:
        update_data["last_name"] = user_update.last_name
    if user_update.middle_name is not None:
        update_data["middle_name"] = user_update.middle_name
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No data provided for update"
        )
    
    # Добавляем время обновления
    update_data["updated_at"] = datetime.utcnow()
    
    # Обновляем пользователя
    stmt = update(User).where(User.id == current_user.id).values(**update_data)
    await db.execute(stmt)
    await db.commit()
    
    # Возвращаем обновленный профиль
    return await get_current_user_profile(current_user, db)


@router.delete("/me", status_code=status.HTTP_200_OK, dependencies=[Depends(security)])
async def delete_current_user_account(
    current_user: User = Depends(get_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Мягкое удаление аккаунта текущего пользователя
    Устанавливает is_active = False (пользователь не может войти в систему)
    Данные остаются в базе данных
    """
    # Мягкое удаление - устанавливаем is_active = False
    stmt = update(User).where(User.id == current_user.id).values(
        is_active=False,
        updated_at=datetime.utcnow()
    )
    await db.execute(stmt)
    await db.commit()
    
    return {
        "message": "Account successfully deactivated",
        "detail": "Your account has been deactivated. You will no longer be able to log in.",
        "user_id": current_user.id,
        "email": current_user.email
    }
