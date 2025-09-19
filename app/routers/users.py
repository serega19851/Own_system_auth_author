# app/routers/users.py
from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPBearer

from app.core_dependencies import get_active_user
from app.dependencies import get_user_profile_service
from app.models import User
from app.schemas.user import UserProfile, UserUpdate
from app.services.user import UserProfileService

router = APIRouter(prefix="/users", tags=["users"])
security = HTTPBearer()


@router.get("/me", response_model=UserProfile, dependencies=[Depends(security)])
async def get_current_user_profile(
    current_user: User = Depends(get_active_user),
    user_profile_service: UserProfileService = Depends(get_user_profile_service)
):
    """Получить профиль текущего пользователя"""
    return await user_profile_service.get_user_profile(current_user.id)


@router.put("/me", response_model=UserProfile, dependencies=[Depends(security)])
async def update_current_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_active_user),
    user_profile_service: UserProfileService = Depends(get_user_profile_service)
):
    """Обновить профиль текущего пользователя"""
    return await user_profile_service.update_user_profile(current_user.id, user_update)


@router.delete("/me", status_code=status.HTTP_200_OK, dependencies=[Depends(security)])
async def delete_current_user_account(
    current_user: User = Depends(get_active_user),
    user_profile_service: UserProfileService = Depends(get_user_profile_service)
):
    """
    Мягкое удаление аккаунта текущего пользователя
    Устанавливает is_active = False (пользователь не может войти в систему)
    Данные остаются в базе данных
    """
    return await user_profile_service.deactivate_user_account(current_user.id)
