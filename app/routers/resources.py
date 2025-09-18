# app/routers/resources.py
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, get_active_user, require_permission
from app.models import User
from app.schemas.resources import (
    DocumentResponse, DocumentCreate, ReportResponse, ReportCreate,
    UserProfilePublic, SystemConfig, PermissionCheckResponse
)

router = APIRouter(prefix="/resources", tags=["resources"])
security = HTTPBearer()

# Mock данные
MOCK_DOCUMENTS = [
    {
        "id": 1,
        "title": "Техническая документация API",
        "content": "Подробное описание всех endpoints системы аутентификации...",
        "author": "admin@test.com",
        "created_at": datetime(2025, 9, 15, 10, 0, 0),
        "is_public": False
    },
    {
        "id": 2,
        "title": "Руководство пользователя",
        "content": "Инструкция по использованию системы для обычных пользователей...",
        "author": "moderator@test.com",
        "created_at": datetime(2025, 9, 16, 14, 30, 0),
        "is_public": True
    },
    {
        "id": 3,
        "title": "Конфиденциальный отчет",
        "content": "Секретная информация доступная только администраторам...",
        "author": "admin@test.com",
        "created_at": datetime(2025, 9, 16, 9, 15, 0),
        "is_public": False
    }
]

MOCK_REPORTS = [
    {
        "id": 1,
        "name": "Статистика пользователей",
        "report_type": "user_stats",
        "data": {"active_users": 4, "inactive_users": 1, "total_logins": 42},
        "generated_at": datetime(2025, 9, 16, 8, 0, 0),
        "generated_by": "admin@test.com"
    },
    {
        "id": 2,
        "name": "Отчет по безопасности",
        "report_type": "security",
        "data": {"failed_logins": 3, "suspicious_activity": 0, "blocked_ips": []},
        "generated_at": datetime(2025, 9, 16, 12, 0, 0),
        "generated_by": "moderator@test.com"
    }
]


@router.get("/documents", response_model=List[DocumentResponse], dependencies=[Depends(security)])
async def get_documents(
    current_user: User = Depends(require_permission("documents_read"))
):
    """
    Получить список документов
    Требует разрешение: documents_read
    """
    return [DocumentResponse(**doc) for doc in MOCK_DOCUMENTS]


@router.post("/documents", response_model=DocumentResponse, dependencies=[Depends(security)])
async def create_document(
    document_data: DocumentCreate,
    current_user: User = Depends(require_permission("documents_write"))
):
    """
    Создать новый документ
    Требует разрешение: documents_write
    """
    new_doc = {
        "id": len(MOCK_DOCUMENTS) + 1,
        "title": document_data.title,
        "content": document_data.content,
        "author": current_user.email,
        "created_at": datetime.utcnow(),
        "is_public": document_data.is_public
    }
    MOCK_DOCUMENTS.append(new_doc)
    return DocumentResponse(**new_doc)


@router.delete("/documents/{document_id}", dependencies=[Depends(security)])
async def delete_document(
    document_id: int,
    current_user: User = Depends(require_permission("documents_delete"))
):
    """
    Удалить документ
    Требует разрешение: documents_delete
    """
    # Ищем документ
    doc_index = None
    for i, doc in enumerate(MOCK_DOCUMENTS):
        if doc["id"] == document_id:
            doc_index = i
            break
    
    if doc_index is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    deleted_doc = MOCK_DOCUMENTS.pop(doc_index)
    return {
        "message": "Document deleted successfully",
        "deleted_document": deleted_doc["title"],
        "deleted_by": current_user.email
    }


@router.get("/reports", response_model=List[ReportResponse], dependencies=[Depends(security)])
async def get_reports(
    current_user: User = Depends(require_permission("reports_read"))
):
    """
    Получить список отчетов
    Требует разрешение: reports_read
    """
    return [ReportResponse(**report) for report in MOCK_REPORTS]


@router.post("/reports", response_model=ReportResponse, dependencies=[Depends(security)])
async def create_report(
    report_data: ReportCreate,
    current_user: User = Depends(require_permission("reports_create"))
):
    """
    Создать новый отчет
    Требует разрешение: reports_create
    """
    new_report = {
        "id": len(MOCK_REPORTS) + 1,
        "name": report_data.name,
        "report_type": report_data.report_type,
        "data": report_data.data,
        "generated_at": datetime.utcnow(),
        "generated_by": current_user.email
    }
    MOCK_REPORTS.append(new_report)
    return ReportResponse(**new_report)


@router.get("/reports/export", dependencies=[Depends(security)])
async def export_reports(
    format: str = "json",
    current_user: User = Depends(require_permission("reports_export"))
):
    """
    Экспортировать отчеты
    Требует разрешение: reports_export
    """
    return {
        "message": f"Reports exported in {format} format",
        "total_reports": len(MOCK_REPORTS),
        "exported_by": current_user.email,
        "export_time": datetime.utcnow(),
        "download_url": f"/downloads/reports_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.{format}"
    }


@router.get("/user-profiles", response_model=List[UserProfilePublic], dependencies=[Depends(security)])
async def get_user_profiles(
    current_user: User = Depends(require_permission("user_profiles_read")),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить список профилей пользователей
    Требует разрешение: user_profiles_read
    """
    # Mock данные профилей
    profiles = [
        {
            "id": 1,
            "full_name": "Админ Главный Системы",
            "email": "admin@test.com",
            "is_active": True,
            "joined_at": datetime(2025, 9, 15, 10, 0, 0)
        },
        {
            "id": 2,
            "full_name": "Иван Сергеевич Петров",
            "email": "user@test.com",
            "is_active": True,
            "joined_at": datetime(2025, 9, 15, 11, 30, 0)
        },
        {
            "id": 3,
            "full_name": "Анна Викторовна Смирнова",
            "email": "moderator@test.com",
            "is_active": True,
            "joined_at": datetime(2025, 9, 15, 12, 15, 0)
        }
    ]
    return [UserProfilePublic(**profile) for profile in profiles]


@router.get("/system/config", response_model=List[SystemConfig], dependencies=[Depends(security)])
async def get_system_config(
    current_user: User = Depends(require_permission("admin_system_config"))
):
    """
    Получить системную конфигурацию
    Требует разрешение: admin_system_config (только админы)
    """
    config = [
        {
            "setting_name": "max_login_attempts",
            "setting_value": "5",
            "description": "Максимальное количество попыток входа",
            "last_modified": datetime(2025, 9, 16, 9, 0, 0),
            "modified_by": "admin@test.com"
        },
        {
            "setting_name": "session_timeout",
            "setting_value": "3600",
            "description": "Время жизни сессии в секундах",
            "last_modified": datetime(2025, 9, 16, 8, 30, 0),
            "modified_by": "admin@test.com"
        },
        {
            "setting_name": "password_min_length",
            "setting_value": "8",
            "description": "Минимальная длина пароля",
            "last_modified": datetime(2025, 9, 15, 15, 45, 0),
            "modified_by": "admin@test.com"
        }
    ]
    return [SystemConfig(**cfg) for cfg in config]


@router.get("/check-permission/{resource_type}/{action}", response_model=PermissionCheckResponse, dependencies=[Depends(security)])
async def check_user_permission(
    resource_type: str,
    action: str,
    current_user: User = Depends(get_active_user)
):
    """
    Проверить, есть ли у пользователя разрешение на действие с ресурсом
    Демонстрационный endpoint для проверки системы прав
    """
    # Собираем все разрешения пользователя
    user_permissions = set()
    for role in current_user.roles:
        for permission in role.permissions:
            user_permissions.add(permission.name)
    
    # Формируем имя проверяемого разрешения
    permission_name = f"{resource_type}_{action}"
    has_permission = permission_name in user_permissions
    
    message = f"User has {'✅' if has_permission else '❌'} permission '{permission_name}'"
    
    return PermissionCheckResponse(
        user_id=current_user.id,
        email=current_user.email,
        resource_type=resource_type,
        action=action,
        has_permission=has_permission,
        user_permissions=list(user_permissions),
        message=message
    )
