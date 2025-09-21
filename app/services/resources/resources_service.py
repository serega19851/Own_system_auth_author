# app/services/resources/resources_service.py

from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.schemas.resources import (
    DocumentResponse, DocumentCreate, ReportResponse, ReportCreate,
    UserProfilePublic, SystemConfig, PermissionCheckResponse
)
from app.repositories.user_repository import UserRepository
from .documents_service import DocumentsService
from .reports_service import ReportsService
from .user_profiles_resource_service import UserProfilesResourceService
from .system_resource_service import SystemResourceService


from ..base_service import BaseService

class ResourcesService(BaseService):
    """Координатор всех ресурсных сервисов"""
    
    def __init__(self, 
                 documents_service: DocumentsService,
                 reports_service: ReportsService,
                 user_profiles_service: UserProfilesResourceService,
                 system_service: SystemResourceService,
                 db: AsyncSession):
        super().__init__()
        self.documents_service = documents_service
        self.reports_service = reports_service
        self.user_profiles_service = user_profiles_service
        self.system_service = system_service
        self.user_repository = UserRepository(db)
    
    # Документы
    async def get_documents(self) -> List[DocumentResponse]:
        """Получить все документы"""
        try:
            return await self.documents_service.get_all_documents()
        except Exception as e:
            self._handle_service_error(e, "get_documents")
            raise
    
    async def create_document(self, document_data: DocumentCreate, author_email: str) -> DocumentResponse:
        """Создать новый документ"""
        try:
            return await self.documents_service.create_document(document_data, author_email)
        except Exception as e:
            self._handle_service_error(e, "create_document")
            raise
    
    async def delete_document(self, document_id: int, user_email: str) -> dict:
        """Удалить документ"""
        try:
            return await self.documents_service.delete_document(document_id, user_email)
        except Exception as e:
            self._handle_service_error(e, "delete_document")
            raise
    
    # Отчеты
    async def get_reports(self) -> List[ReportResponse]:
        """Получить все отчеты"""
        try:
            return await self.reports_service.get_all_reports()
        except Exception as e:
            self._handle_service_error(e, "get_reports")
            raise
    
    async def create_report(self, report_data: ReportCreate, author_email: str) -> ReportResponse:
        """Создать новый отчет"""
        try:
            return await self.reports_service.create_report(report_data, author_email)
        except Exception as e:
            self._handle_service_error(e, "create_report")
            raise
    
    async def export_reports(self, user_email: str) -> dict:
        """Экспортировать отчеты"""
        try:
            return await self.reports_service.export_reports(user_email)
        except Exception as e:
            self._handle_service_error(e, "export_reports")
            raise
    
    # Профили пользователей
    async def get_user_profiles(self) -> List[UserProfilePublic]:
        """Получить профили пользователей"""
        try:
            return await self.user_profiles_service.get_all_profiles()
        except Exception as e:
            self._handle_service_error(e, "get_user_profiles")
            raise
    
    # Системная конфигурация
    async def get_system_config(self) -> List[SystemConfig]:
        """Получить системную конфигурацию"""
        try:
            return await self.system_service.get_system_config()
        except Exception as e:
            self._handle_service_error(e, "get_system_config")
            raise
    
    # Проверка разрешений
    async def check_permission(self, user: User, resource: str, action: str) -> PermissionCheckResponse:
        """
        Проверить разрешение пользователя
        Собственная логика проверки через репозиторий
        """
        try:
            # Получаем пользователя с полной информацией о ролях и разрешениях
            user_with_permissions = await self.user_repository.get_user_with_roles_and_permissions(user.id)
            
            if not user_with_permissions:
                return PermissionCheckResponse(
                    has_permission=False,
                    resource_type=resource,
                    action=action,
                    user_id=user.id,
                    message="Пользователь не найден"
                )
            
            # Проверяем активность пользователя
            if not user_with_permissions.is_active:
                return PermissionCheckResponse(
                    has_permission=False,
                    resource_type=resource,
                    action=action,
                    user_id=user.id,
                    message="Пользователь неактивен"
                )
            
            # Собираем все разрешения пользователя из всех его ролей
            user_permissions = []
            for role in user_with_permissions.roles:
                if role.is_active:  # Проверяем только активные роли
                    for permission in role.permissions:
                        user_permissions.append(permission)
            
            # Формируем имя разрешения в формате "resource_action"
            required_permission_name = f"{resource}_{action}"
            
            # Проверяем наличие требуемого разрешения
            has_permission = any(
                perm.name == required_permission_name or 
                (perm.resource_type == resource and perm.action == action)
                for perm in user_permissions
            )
            
            return PermissionCheckResponse(
                has_permission=has_permission,
                resource_type=resource,
                action=action,
                user_id=user.id,
                message="Доступ разрешен" if has_permission else f"Нет разрешения '{required_permission_name}'"
            )
            
        except Exception as e:
            self._handle_service_error(e, "check_permission")
            raise
