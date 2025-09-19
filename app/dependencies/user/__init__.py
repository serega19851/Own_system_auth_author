"""
Пакет зависимостей для пользовательских сервисов
Содержит фабрики для создания пользовательских сервисов по образцу админской архитектуры
"""

from .user_profile_dependencies import (
    UserProfileDependencyFactory,
    get_user_profile_service,
    get_user_auth_service
)

__all__ = [
    "UserProfileDependencyFactory",
    "get_user_profile_service", 
    "get_user_auth_service"
]
