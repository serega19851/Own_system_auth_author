from .system_exceptions import SystemException

class DatabaseException(SystemException):
    """Ошибки работы с базой данных"""
    pass

class ConnectionException(DatabaseException):
    """Ошибки подключения к БД"""
    pass

class IntegrityException(DatabaseException):
    """Ошибки целостности данных"""
    pass

class QueryException(DatabaseException):
    """Ошибки выполнения запросов"""
    pass
