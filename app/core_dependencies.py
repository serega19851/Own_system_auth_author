# app/core_dependencies.py
from typing import Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import User, Role
from app.auth import get_jwt_service, JWTService

# Настройка безопасности (опциональная для поддержки cookies)
security = HTTPBearer(auto_error=False)


# Пользовательские зависимости перенесены в app.dependencies.user


def get_token_from_request(
    request: Request, 
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[str]:
    """
    Получение JWT токена из запроса (из Bearer header или HTTP-only cookie)
    Приоритет: Bearer токен > Cookie
    """
    # Сначала проверяем Bearer токен в заголовке
    if credentials and credentials.credentials:
        return credentials.credentials
    
    # Если Bearer токена нет, проверяем cookie
    access_token = request.cookies.get("access_token")
    if access_token:
        return access_token
    
    return None


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
    jwt_service: JWTService = Depends(get_jwt_service),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> User:
    """
    Получение текущего пользователя из JWT токена (Bearer или Cookie)
    """
    # Получаем токен из запроса
    token = get_token_from_request(request, credentials)
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization credentials required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Декодирование JWT токена
    token_data = jwt_service.verify_token(token)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Получаем email из токена
    email = token_data.get("sub")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Поиск пользователя в базе данных с загрузкой ролей
    stmt = select(User).options(selectinload(User.roles)).where(User.email == email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def get_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Получение активного пользователя
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    return current_user


async def get_admin_user(current_user: User = Depends(get_active_user)) -> User:
    """
    Получение пользователя с правами администратора
    """
    # Проверяем, есть ли у пользователя роль admin
    user_role_names = [role.name for role in current_user.roles]
    
    if "admin" not in user_role_names:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return current_user


def require_permission(permission_name: str):
    """
    Фабрика зависимости для проверки конкретного разрешения
    
    Args:
        permission_name: Название разрешения (например, "documents_read")
    
    Returns:
        Dependency function для использования в роутах
    """
    async def permission_dependency(
        current_user: User = Depends(get_active_user),
        db: AsyncSession = Depends(get_db)
    ) -> User:
        # Проверяем разрешения через роли пользователя
        user_permissions = []
        for role in current_user.roles:
            # Загружаем разрешения для каждой роли
            stmt = select(Role).options(selectinload(Role.permissions)).where(Role.id == role.id)
            result = await db.execute(stmt)
            role_with_permissions = result.scalar_one_or_none()
            
            if role_with_permissions:
                for permission in role_with_permissions.permissions:
                    user_permissions.append(permission.name)
        
        # Проверяем наличие требуемого разрешения
        if permission_name not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission_name}' required"
            )
        
        return current_user
    
    return permission_dependency
