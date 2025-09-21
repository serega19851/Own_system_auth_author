# app/routers/resources.py
from typing import List
from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer

from app.dependencies import get_active_user, require_permission, get_resources_service
from app.models import User
from app.schemas.resources import (
    DocumentResponse, DocumentCreate, ReportResponse, ReportCreate,
    UserProfilePublic, SystemConfig
)
from app.services.resources import ResourcesService

router = APIRouter(prefix="/resources", tags=["resources"])
security = HTTPBearer()


@router.get("/documents", response_model=List[DocumentResponse], dependencies=[Depends(security)])
async def get_documents(
    resources_service: ResourcesService = Depends(get_resources_service)
):
    """Получить список документов"""
    return await resources_service.get_documents()


@router.post("/documents", response_model=DocumentResponse, dependencies=[Depends(security)])
async def create_document(
    document_data: DocumentCreate,
    current_user: User = Depends(require_permission("documents_write")),
    resources_service: ResourcesService = Depends(get_resources_service)
):
    """Создать новый документ"""
    return await resources_service.create_document(document_data, current_user.email)


@router.delete("/documents/{document_id}", dependencies=[Depends(security)])
async def delete_document(
    document_id: int,
    current_user: User = Depends(require_permission("documents_delete")),
    resources_service: ResourcesService = Depends(get_resources_service)
):
    """Удалить документ"""
    return await resources_service.delete_document(document_id, current_user.email)


@router.get("/reports", response_model=List[ReportResponse], dependencies=[Depends(security)])
async def get_reports(
    resources_service: ResourcesService = Depends(get_resources_service)
):
    """Получить список отчетов"""
    return await resources_service.get_reports()


@router.post("/reports", response_model=ReportResponse, dependencies=[Depends(security)])
async def create_report(
    report_data: ReportCreate,
    current_user: User = Depends(require_permission("reports_create")),
    resources_service: ResourcesService = Depends(get_resources_service)
):
    """Создать новый отчет"""
    return await resources_service.create_report(report_data, current_user.email)


@router.get("/reports/export", dependencies=[Depends(security)])
async def export_reports(
    format: str = "json",
    current_user: User = Depends(require_permission("reports_export")),
    resources_service: ResourcesService = Depends(get_resources_service)
):
    """Экспортировать отчеты"""
    return await resources_service.export_reports(format, current_user.email)


@router.get("/user-profiles", response_model=List[UserProfilePublic], dependencies=[Depends(security)])
async def get_user_profiles(
    resources_service: ResourcesService = Depends(get_resources_service)
):
    """Получить список профилей пользователей"""
    return await resources_service.get_user_profiles()


@router.get("/system/config", response_model=List[SystemConfig])
async def get_system_config(
    current_user: User = Depends(require_permission("admin_system_config")),
    resources_service: ResourcesService = Depends(get_resources_service)
):
    """Получить системную конфигурацию - ТРЕБУЕТ РАЗРЕШЕНИЕ admin_system_config"""
    return await resources_service.get_system_config()



