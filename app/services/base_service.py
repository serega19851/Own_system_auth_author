from abc import ABC
from ..utils.logger import get_logger
from ..exceptions.system_exceptions import SystemException

class BaseService(ABC):
    """Базовый класс для всех сервисов с единообразной обработкой ошибок"""
    
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
    
    def _handle_service_error(self, error: Exception, operation: str) -> None:
        """Централизованная обработка ошибок сервиса"""
        self.logger.error(f"Service error in {operation}: {str(error)}")
        
        if isinstance(error, SystemException):
            raise error
        else:
            raise SystemException(f"Ошибка при выполнении операции: {operation}")
