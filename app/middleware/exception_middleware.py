from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from ..handlers.exception_handlers import GlobalExceptionHandler
from ..utils.logger import get_logger

logger = get_logger(__name__)

class ExceptionMiddleware(BaseHTTPMiddleware):
    """Middleware для глобальной обработки исключений"""
    
    async def dispatch(self, request: Request, call_next) -> Response:
        try:
            response = await call_next(request)
            return response
        except Exception as exc:
            logger.error(f"Unhandled exception in middleware: {str(exc)}", exc_info=True)
            return await GlobalExceptionHandler.generic_exception_handler(request, exc)
