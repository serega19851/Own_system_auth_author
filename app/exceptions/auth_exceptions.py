from .system_exceptions import SystemException

class AuthenticationException(SystemException):
    """Ошибки аутентификации"""
    pass

class AuthorizationException(SystemException):
    """Ошибки авторизации"""
    pass

class TokenException(SystemException):
    """Ошибки работы с токенами"""
    pass

class PasswordException(SystemException):
    """Ошибки работы с паролями"""
    pass
