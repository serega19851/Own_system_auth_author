"""
Исключения для валидации бизнес-правил системы
Содержит специфичные исключения для валидаторов
"""

from .business_exceptions import UserException, RoleException, PermissionException
from .system_exceptions import ValidationException


class UserNotFoundException(UserException):
    """Исключение: пользователь не найден"""
    pass


class RoleNotFoundException(RoleException):
    """Исключение: роль не найдена"""
    pass


class RoleAlreadyExistsException(RoleException):
    """Исключение: роль уже существует"""
    pass


class PermissionNotFoundException(PermissionException):
    """Исключение: разрешение не найдено"""
    pass


class InvalidRoleAssignmentException(ValidationException):
    """Исключение: некорректное назначение роли"""
    pass
