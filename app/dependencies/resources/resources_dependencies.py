# app/dependencies/resources/resources_dependencies.py

from fastapi import Depends

from app.services.resources import (
    ResourcesService, DocumentsService, ReportsService,
    UserProfilesResourceService, SystemResourceService, PermissionCheckService
)


class ResourcesDependencyFactory:
    """Фабрика для создания зависимостей ресурсов"""
    
    @staticmethod
    def create_documents_service() -> DocumentsService:
        """Создать сервис документов"""
        return DocumentsService()
    
    @staticmethod  
    def create_reports_service() -> ReportsService:
        """Создать сервис отчетов"""
        return ReportsService()
    
    @staticmethod
    def create_user_profiles_service() -> UserProfilesResourceService:
        """Создать сервис профилей пользователей"""
        return UserProfilesResourceService()
    
    @staticmethod
    def create_system_service() -> SystemResourceService:
        """Создать сервис системной конфигурации"""
        return SystemResourceService()
    
    @staticmethod
    def create_permission_check_service() -> PermissionCheckService:
        """Создать сервис проверки разрешений"""
        return PermissionCheckService()
    
    @staticmethod
    def create_resources_service(
        documents_service: DocumentsService,
        reports_service: ReportsService,
        user_profiles_service: UserProfilesResourceService,
        system_service: SystemResourceService,
        permission_check_service: PermissionCheckService
    ) -> ResourcesService:
        """Создать координатор ресурсов"""
        return ResourcesService(
            documents_service=documents_service,
            reports_service=reports_service,
            user_profiles_service=user_profiles_service,
            system_service=system_service,
            permission_check_service=permission_check_service
        )


async def get_resources_service() -> ResourcesService:
    """Dependency для получения ResourcesService"""
    factory = ResourcesDependencyFactory()
    
    # Создание всех специализированных сервисов
    documents_service = factory.create_documents_service()
    reports_service = factory.create_reports_service()
    user_profiles_service = factory.create_user_profiles_service()
    system_service = factory.create_system_service()
    permission_check_service = factory.create_permission_check_service()
    
    # Создание координатора ресурсов
    return factory.create_resources_service(
        documents_service=documents_service,
        reports_service=reports_service,
        user_profiles_service=user_profiles_service,
        system_service=system_service,
        permission_check_service=permission_check_service
    )
