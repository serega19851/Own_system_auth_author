# app/schemas/resources.py
from datetime import datetime
from typing import List
from pydantic import BaseModel


class DocumentResponse(BaseModel):
    """Mock документ"""
    id: int
    title: str
    content: str
    author: str
    created_at: datetime
    is_public: bool


class DocumentCreate(BaseModel):
    """Схема создания документа"""
    title: str
    content: str
    is_public: bool = False


class ReportResponse(BaseModel):
    """Mock отчет"""
    id: int
    name: str
    report_type: str
    data: dict
    generated_at: datetime
    generated_by: str


class ReportCreate(BaseModel):
    """Схема создания отчета"""
    name: str
    report_type: str
    data: dict


class UserProfilePublic(BaseModel):
    """Публичная информация профиля пользователя"""
    id: int
    full_name: str
    email: str
    is_active: bool
    joined_at: datetime


class SystemConfig(BaseModel):
    """Mock системная конфигурация"""
    setting_name: str
    setting_value: str
    description: str
    last_modified: datetime
    modified_by: str


class PermissionCheckResponse(BaseModel):
    """Ответ проверки прав доступа"""
    user_id: int
    email: str
    resource_type: str
    action: str
    has_permission: bool
    user_permissions: List[str]
    message: str
