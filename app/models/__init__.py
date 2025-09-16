# app/models/__init__.py
"""
Модели системы аутентификации и авторизации (RBAC)
"""

# Импорт Base для экспорта
from app.database import Base

# Импорт связующих таблиц (должны быть импортированы первыми)
from app.models.associations import user_roles, role_permissions

# Импорт всех моделей для Alembic autogenerate
from app.models.user import User
from app.models.role import Role
from app.models.permission import Permission
from app.models.resource import Resource