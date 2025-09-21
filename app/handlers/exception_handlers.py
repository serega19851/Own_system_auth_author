from fastapi import Request, HTTPException
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

from ..exceptions import (
    SystemException, AuthenticationException, AuthorizationException,
    ValidationException, ResourceNotFoundException
)
from ..utils.logger import get_logger
from .error_responses import ErrorResponseBuilder

logger = get_logger(__name__)

class GlobalExceptionHandler:
    """Централизованный обработчик исключений"""
    
    @staticmethod
    async def system_exception_handler(request: Request, exc: SystemException):
        """Обработка системных исключений"""
        logger.error(f"System exception: {exc.message}", extra={
            "error_code": exc.error_code,
            "path": request.url.path,
            "method": request.method
        })
        
        return ErrorResponseBuilder.build_error_response(
            message=exc.message,
            error_code=exc.error_code,
            status_code=400
        )
    
    @staticmethod
    async def auth_exception_handler(request: Request, exc: AuthenticationException):
        """Обработка ошибок аутентификации"""
        logger.warning(f"Authentication error: {exc.message}")
        
        return ErrorResponseBuilder.build_error_response(
            message=exc.message,
            error_code=exc.error_code,
            status_code=401
        )
    
    @staticmethod
    async def authorization_exception_handler(request: Request, exc: AuthorizationException):
        """Обработка ошибок авторизации"""
        logger.warning(f"Authorization error: {exc.message}")
        
        return ErrorResponseBuilder.build_error_response(
            message=exc.message,
            error_code=exc.error_code,
            status_code=403
        )
    
    @staticmethod
    async def validation_exception_handler(request: Request, exc: ValidationException):
        """Обработка ошибок валидации"""
        logger.info(f"Validation error: {exc.message}")
        
        return ErrorResponseBuilder.build_error_response(
            message=exc.message,
            error_code=exc.error_code,
            status_code=422
        )
    
    @staticmethod
    async def resource_not_found_handler(request: Request, exc: ResourceNotFoundException):
        """Обработка ошибок 'ресурс не найден'"""
        logger.info(f"Resource not found: {exc.message}")
        
        return ErrorResponseBuilder.build_error_response(
            message=exc.message,
            error_code=exc.error_code,
            status_code=404
        )
    
    @staticmethod
    async def database_exception_handler(request: Request, exc: SQLAlchemyError):
        """Обработка ошибок базы данных"""
        logger.error(f"Database error: {str(exc)}")
        
        return ErrorResponseBuilder.build_error_response(
            message="Ошибка при работе с базой данных",
            error_code="DATABASE_ERROR",
            status_code=500
        )
    
    @staticmethod
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        """Обработка ошибок валидации FastAPI"""
        logger.info(f"FastAPI validation error: {exc.errors()}")
        
        return ErrorResponseBuilder.build_error_response(
            message="Ошибка валидации входных данных",
            error_code="VALIDATION_ERROR",
            status_code=422,
            details=exc.errors()
        )
    
    @staticmethod
    async def http_exception_handler(request: Request, exc: HTTPException):
        """Обработка HTTP исключений"""
        logger.info(f"HTTP exception: {exc.detail}")
        
        return ErrorResponseBuilder.build_error_response(
            message=exc.detail,
            error_code="HTTP_ERROR",
            status_code=exc.status_code
        )
    
    @staticmethod
    async def generic_exception_handler(request: Request, exc: Exception):
        """Обработка всех остальных исключений"""
        logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
        
        return ErrorResponseBuilder.build_error_response(
            message="Внутренняя ошибка сервера",
            error_code="INTERNAL_ERROR",
            status_code=500
        )
