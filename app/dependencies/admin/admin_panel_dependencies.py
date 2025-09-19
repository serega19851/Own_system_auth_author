"""
Dependency Injection Factory для админ-панели
Создает и настраивает всю иерархию сервисов для административных операций
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from ...models.user import User
from ...models.role import Role
from ...models.permission import Permission
from ...models.resource import Resource

# Репозитории
from ...repositories import (
    UserRepository,
    RoleRepository,
    PermissionRepository,
    ResourceRepository
)

# Утилиты
from ...mappers import SystemMappers
from ...validators import SystemValidators

# Сервисы (прямой импорт для избежания циклических зависимостей)
from ...services.admin.system_statistics_service import SystemStatisticsService
from ...services.admin.user_management_service import UserManagementService
from ...services.admin.role_management_service import RoleManagementService
from ...services.admin.permission_service import PermissionService
from ...services.admin.admin_panel_service import AdminPanelService


class AdminPanelDependencyFactory:
    """
    Фабрика зависимостей для админ-панели
    Создает и настраивает всю иерархию сервисов с правильными зависимостями
    """
    
    @staticmethod
    def create_user_repository(db: AsyncSession) -> UserRepository:
        """Создать репозиторий пользователей"""
        return UserRepository(db)
    
    @staticmethod
    def create_role_repository(db: AsyncSession) -> RoleRepository:
        """Создать репозиторий ролей"""
        return RoleRepository(db)
    
    @staticmethod
    def create_permission_repository(db: AsyncSession) -> PermissionRepository:
        """Создать репозиторий разрешений"""
        return PermissionRepository(db)
    
    @staticmethod
    def create_resource_repository(db: AsyncSession) -> ResourceRepository:
        """Создать репозиторий ресурсов"""
        return ResourceRepository(db)
    
    @staticmethod
    def create_system_mappers() -> SystemMappers:
        """Создать мапперы системы"""
        return SystemMappers()
    
    @staticmethod
    def create_system_validators() -> SystemValidators:
        """Создать валидаторы системы"""
        return SystemValidators()
    
    @staticmethod
    def create_system_statistics_service(
        user_repo: UserRepository,
        role_repo: RoleRepository,
        permission_repo: PermissionRepository,
        resource_repo: ResourceRepository
    ) -> SystemStatisticsService:
        """Создать сервис статистики системы"""
        return SystemStatisticsService(
            user_repo=user_repo,
            role_repo=role_repo,
            permission_repo=permission_repo,
            resource_repo=resource_repo
        )
    
    @staticmethod
    def create_user_management_service(
        user_repo: UserRepository,
        role_repo: RoleRepository,
        validators: SystemValidators,
        mappers: SystemMappers
    ) -> UserManagementService:
        """Создать сервис управления пользователями"""
        return UserManagementService(
            user_repo=user_repo,
            role_repo=role_repo,
            validators=validators,
            mappers=mappers
        )
    
    @staticmethod
    def create_role_management_service(
        role_repo: RoleRepository,
        permission_repo: PermissionRepository,
        validators: SystemValidators,
        mappers: SystemMappers
    ) -> RoleManagementService:
        """Создать сервис управления ролями"""
        return RoleManagementService(
            role_repo=role_repo,
            permission_repo=permission_repo,
            validators=validators,
            mappers=mappers
        )
    
    @staticmethod
    def create_permission_service(
        permission_repo: PermissionRepository,
        mappers: SystemMappers
    ) -> PermissionService:
        """Создать сервис управления разрешениями"""
        return PermissionService(
            permission_repo=permission_repo,
            mappers=mappers
        )
    
    @staticmethod
    def create_admin_panel_service(
        statistics_service: SystemStatisticsService,
        user_management_service: UserManagementService,
        role_management_service: RoleManagementService,
        permission_service: PermissionService
    ) -> AdminPanelService:
        """Создать главный сервис админ-панели"""
        return AdminPanelService(
            statistics_service=statistics_service,
            user_management_service=user_management_service,
            role_management_service=role_management_service,
            permission_service=permission_service
        )


# ============================================================================
# DEPENDENCY INJECTION FUNCTIONS
# ============================================================================

async def get_admin_panel_service(db: AsyncSession = Depends(get_db)) -> AdminPanelService:
    """
    Главная функция для получения AdminPanelService со всеми зависимостями
    
    Создает полную иерархию:
    Repositories -> Mappers/Validators -> Specialized Services -> AdminPanelService
    
    Args:
        db: Сессия базы данных
        
    Returns:
        AdminPanelService: Полностью настроенный сервис админ-панели
    """
    factory = AdminPanelDependencyFactory()
    
    # ========================================
    # СОЗДАНИЕ РЕПОЗИТОРИЕВ
    # ========================================
    user_repo = factory.create_user_repository(db)
    role_repo = factory.create_role_repository(db)
    permission_repo = factory.create_permission_repository(db)
    resource_repo = factory.create_resource_repository(db)
    
    # ========================================
    # СОЗДАНИЕ УТИЛИТ
    # ========================================
    mappers = factory.create_system_mappers()
    validators = factory.create_system_validators()
    
    # ========================================
    # СОЗДАНИЕ СПЕЦИАЛИЗИРОВАННЫХ СЕРВИСОВ
    # ========================================
    statistics_service = factory.create_system_statistics_service(
        user_repo, role_repo, permission_repo, resource_repo
    )
    
    user_management_service = factory.create_user_management_service(
        user_repo, role_repo, validators, mappers
    )
    
    role_management_service = factory.create_role_management_service(
        role_repo, permission_repo, validators, mappers
    )
    
    permission_service = factory.create_permission_service(
        permission_repo, mappers
    )
    
    # ========================================
    # СОЗДАНИЕ ГЛАВНОГО КООРДИНАТОРА
    # ========================================
    admin_panel_service = factory.create_admin_panel_service(
        statistics_service,
        user_management_service,
        role_management_service,
        permission_service
    )
    
    return admin_panel_service


# ============================================================================
# ОТДЕЛЬНЫЕ ЗАВИСИМОСТИ ДЛЯ СПЕЦИАЛИЗИРОВАННЫХ СЕРВИСОВ
# ============================================================================

async def get_system_statistics_service(db: AsyncSession = Depends(get_db)) -> SystemStatisticsService:
    """Получить сервис статистики системы"""
    factory = AdminPanelDependencyFactory()
    
    user_repo = factory.create_user_repository(db)
    role_repo = factory.create_role_repository(db)
    permission_repo = factory.create_permission_repository(db)
    resource_repo = factory.create_resource_repository(db)
    
    return factory.create_system_statistics_service(
        user_repo, role_repo, permission_repo, resource_repo
    )


async def get_user_management_service(db: AsyncSession = Depends(get_db)) -> UserManagementService:
    """Получить сервис управления пользователями"""
    factory = AdminPanelDependencyFactory()
    
    user_repo = factory.create_user_repository(db)
    role_repo = factory.create_role_repository(db)
    mappers = factory.create_system_mappers()
    validators = factory.create_system_validators()
    
    return factory.create_user_management_service(
        user_repo, role_repo, validators, mappers
    )


async def get_role_management_service(db: AsyncSession = Depends(get_db)) -> RoleManagementService:
    """Получить сервис управления ролями"""
    factory = AdminPanelDependencyFactory()
    
    role_repo = factory.create_role_repository(db)
    permission_repo = factory.create_permission_repository(db)
    mappers = factory.create_system_mappers()
    validators = factory.create_system_validators()
    
    return factory.create_role_management_service(
        role_repo, permission_repo, validators, mappers
    )


async def get_permission_service(db: AsyncSession = Depends(get_db)) -> PermissionService:
    """Получить сервис управления разрешениями"""
    factory = AdminPanelDependencyFactory()
    
    permission_repo = factory.create_permission_repository(db)
    mappers = factory.create_system_mappers()
    
    return factory.create_permission_service(permission_repo, mappers)


# ============================================================================
# ВСПОМОГАТЕЛЬНЫЕ ЗАВИСИМОСТИ
# ============================================================================

async def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
    """Получить репозиторий пользователей"""
    return AdminPanelDependencyFactory.create_user_repository(db)


async def get_role_repository(db: AsyncSession = Depends(get_db)) -> RoleRepository:
    """Получить репозиторий ролей"""
    return AdminPanelDependencyFactory.create_role_repository(db)


async def get_permission_repository(db: AsyncSession = Depends(get_db)) -> PermissionRepository:
    """Получить репозиторий разрешений"""
    return AdminPanelDependencyFactory.create_permission_repository(db)


async def get_resource_repository(db: AsyncSession = Depends(get_db)) -> ResourceRepository:
    """Получить репозиторий ресурсов"""
    return AdminPanelDependencyFactory.create_resource_repository(db)


def get_system_mappers() -> SystemMappers:
    """Получить мапперы системы"""
    return AdminPanelDependencyFactory.create_system_mappers()


def get_system_validators() -> SystemValidators:
    """Получить валидаторы системы"""
    return AdminPanelDependencyFactory.create_system_validators()
