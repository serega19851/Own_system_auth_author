from .system_exceptions import SystemException

class UserException(SystemException):
    """Исключения связанные с пользователями"""
    pass

class RoleException(SystemException):
    """Исключения связанные с ролями"""
    pass

class PermissionException(SystemException):
    """Исключения связанные с разрешениями"""
    pass

class ResourceException(SystemException):
    """Исключения связанные с ресурсами"""
    pass
