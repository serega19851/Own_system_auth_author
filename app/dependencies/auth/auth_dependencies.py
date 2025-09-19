"""
Фабрика зависимостей для домена аутентификации
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.auth import AuthService
from app.services.user.user_auth_service import UserService
from app.auth import JWTService, CookieService, get_jwt_service, get_cookie_service


class AuthDependencyFactory:
    """Фабрика для создания зависимостей домена аутентификации"""
    
    @staticmethod
    def create_user_service(db: AsyncSession) -> UserService:
        """Создание сервиса пользователей"""
        return UserService(db)
    
    @staticmethod
    def create_jwt_service() -> JWTService:
        """Создание JWT сервиса"""
        return JWTService()
    
    @staticmethod
    def create_cookie_service() -> CookieService:
        """Создание Cookie сервиса"""
        return CookieService()
    
    @staticmethod
    def create_auth_service(
        user_service: UserService,
        jwt_service: JWTService, 
        cookie_service: CookieService
    ) -> AuthService:
        """Создание координирующего сервиса аутентификации"""
        return AuthService(user_service, jwt_service, cookie_service)


async def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    """
    Dependency для получения AuthService с полным набором зависимостей
    
    Создает:
    - UserService для работы с пользователями
    - JWTService для работы с токенами  
    - CookieService для работы с cookies
    - AuthService как координатор всех операций аутентификации
    """
    # Создание базовых сервисов
    user_service = AuthDependencyFactory.create_user_service(db)
    jwt_service = AuthDependencyFactory.create_jwt_service()
    cookie_service = AuthDependencyFactory.create_cookie_service()
    
    # Создание координирующего сервиса
    return AuthDependencyFactory.create_auth_service(
        user_service, jwt_service, cookie_service
    )
