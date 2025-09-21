from typing import Optional, Dict, Any
from fastapi.responses import JSONResponse
from datetime import datetime

class ErrorResponseBuilder:
    """Строитель стандартизированных ответов об ошибках"""
    
    @staticmethod
    def build_error_response(
        message: str,
        error_code: Optional[str] = None,
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None
    ) -> JSONResponse:
        """
        Создание стандартизированного ответа об ошибке
        
        Args:
            message: Сообщение об ошибке
            error_code: Код ошибки
            status_code: HTTP статус код
            details: Дополнительные детали ошибки
        """
        error_response = {
            "error": True,
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
            "status_code": status_code
        }
        
        if error_code:
            error_response["error_code"] = error_code
        
        if details:
            error_response["details"] = details
        
        return JSONResponse(
            status_code=status_code,
            content=error_response
        )
