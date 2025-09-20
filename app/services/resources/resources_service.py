# app/services/resources/resources_service.py

from typing import List

from app.models import User
from app.schemas.resources import (
    DocumentResponse, DocumentCreate, ReportResponse, ReportCreate,
    UserProfilePublic, SystemConfig, PermissionCheckResponse
)
from .documents_service import DocumentsService
from .reports_service import ReportsService
from .user_profiles_resource_service import UserProfilesResourceService
from .system_resource_service import SystemResourceService
from .permission_check_service import PermissionCheckService


class ResourcesService:
    """Координатор всех ресурсных сервисов"""
    
    def __init__(self, 
                 documents_service: DocumentsService,
                 reports_service: ReportsService,
                 user_profiles_service: UserProfilesResourceService,
                 system_service: SystemResourceService,
                 permission_check_service: PermissionCheckService):
        self.documents_service = documents_service
        self.reports_service = reports_service
        self.user_profiles_service = user_profiles_service
        self.system_service = system_service
        self.permission_check_service = permission_check_service
    
    # === Documents Methods ===
    async def get_documents(self) -> List[DocumentResponse]:
        """Получить все документы"""
        return await self.documents_service.get_all_documents()
    
    async def create_document(self, document_data: DocumentCreate, author_email: str) -> DocumentResponse:
        """Создать новый документ"""
        return await self.documents_service.create_document(document_data, author_email)
    
    async def delete_document(self, document_id: int, user_email: str) -> dict:
        """Удалить документ"""
        return await self.documents_service.delete_document(document_id, user_email)
    
    # === Reports Methods ===
    async def get_reports(self) -> List[ReportResponse]:
        """Получить все отчеты"""
        return await self.reports_service.get_all_reports()
    
    async def create_report(self, report_data: ReportCreate, generator_email: str) -> ReportResponse:
        """Создать новый отчет"""
        return await self.reports_service.create_report(report_data, generator_email)
    
    async def export_reports(self, format: str, user_email: str) -> dict:
        """Экспортировать отчеты"""
        return await self.reports_service.export_reports(format, user_email)
    
    # === User Profiles Methods ===
    async def get_user_profiles(self) -> List[UserProfilePublic]:
        """Получить профили пользователей"""
        return await self.user_profiles_service.get_user_profiles()
    
    # === System Methods ===
    async def get_system_config(self) -> List[SystemConfig]:
        """Получить системную конфигурацию"""
        return await self.system_service.get_system_config()
    
    # === Permission Check Methods ===
    async def check_permission(self, user: User, resource_type: str, action: str) -> PermissionCheckResponse:
        """Проверить разрешение пользователя"""
        return await self.permission_check_service.check_user_permission(user, resource_type, action)
