"""
Зависимости для домена аутентификации
"""

from .auth_dependencies import (
    AuthDependencyFactory,
    get_auth_service
)

__all__ = [
    "AuthDependencyFactory", 
    "get_auth_service"
]
