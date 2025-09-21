class SystemException(Exception):
    """Базовое исключение системы"""
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

class ValidationException(SystemException):
    """Ошибки валидации данных"""
    pass

class BusinessRuleException(SystemException):
    """Нарушение бизнес-правил"""
    pass

class ResourceNotFoundException(SystemException):
    """Ресурс не найден"""
    pass

class AccessDeniedException(SystemException):
    """Доступ запрещен"""
    pass
