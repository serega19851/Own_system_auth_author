"""
Dependency Injection Factory для пользовательских сервисов
Создает и настраивает иерархию сервисов для пользовательских операций
По образцу AdminPanelDependencyFactory
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db

# Репозитории
from ...repositories.user_repository import UserRepository

# Утилиты
from ...mappers.system_mappers import SystemMappers
from ...validators.system_validators import SystemValidators

# Сервисы
from ...services.user.user_profile_service import UserProfileService
from ...services.user.user_auth_service import UserService


class UserProfileDependencyFactory:
    """
    Фабрика зависимостей для пользовательских сервисов
    Создает и настраивает иерархию сервисов с правильными зависимостями
    По образцу AdminPanelDependencyFactory
    """
    
    @staticmethod
    def create_user_repository(db: AsyncSession) -> UserRepository:
        """Создать репозиторий пользователей"""
        return UserRepository(db)
    
    @staticmethod
    def create_system_mappers() -> SystemMappers:
        """Создать мапперы системы"""
        return SystemMappers()
    
    @staticmethod
    def create_system_validators() -> SystemValidators:
        """Создать валидаторы системы"""
        return SystemValidators()
    
    @staticmethod
    def create_user_profile_service(
        user_repo: UserRepository,
        mappers: SystemMappers,
        validators: SystemValidators
    ) -> UserProfileService:
        """Создать сервис управления профилями"""
        return UserProfileService(user_repo, mappers, validators)
    
    @staticmethod
    def create_user_auth_service(db: AsyncSession) -> UserService:
        """Создать сервис аутентификации"""
        return UserService(db)


# ============================================================================
# ОСНОВНЫЕ ЗАВИСИМОСТИ ДЛЯ ПОЛЬЗОВАТЕЛЬСКИХ СЕРВИСОВ
# ============================================================================

async def get_user_profile_service(db: AsyncSession = Depends(get_db)) -> UserProfileService:
    """
    Главная функция для получения UserProfileService со всеми зависимостями
    
    Создает иерархию:
    Repository -> Mappers/Validators -> UserProfileService
    
    Args:
        db: Сессия базы данных
        
    Returns:
        UserProfileService: Полностью настроенный сервис профилей
    """
    factory = UserProfileDependencyFactory()
    
    # ========================================
    # СОЗДАНИЕ РЕПОЗИТОРИЯ
    # ========================================
    user_repo = factory.create_user_repository(db)
    
    # ========================================
    # СОЗДАНИЕ УТИЛИТ
    # ========================================
    mappers = factory.create_system_mappers()
    validators = factory.create_system_validators()
    
    # ========================================
    # СОЗДАНИЕ СЕРВИСА
    # ========================================
    user_profile_service = factory.create_user_profile_service(
        user_repo, mappers, validators
    )
    
    return user_profile_service


async def get_user_auth_service(db: AsyncSession = Depends(get_db)) -> UserService:
    """
    Получить сервис аутентификации пользователей
    
    Args:
        db: Сессия базы данных
        
    Returns:
        UserService: Сервис аутентификации
    """
    factory = UserProfileDependencyFactory()
    return factory.create_user_auth_service(db)
