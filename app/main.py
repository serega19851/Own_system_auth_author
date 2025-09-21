# app/main.py
from fastapi import FastAPI
from fastapi.security import HTTPBearer
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.routers import users, admin, resources, auth
from app.handlers.exception_handlers import GlobalExceptionHandler
from app.exceptions import (
    SystemException, AuthenticationException, AuthorizationException,
    ValidationException, ResourceNotFoundException
)
from app.middleware.exception_middleware import ExceptionMiddleware
from app.utils.logger import setup_logging

# Настройка логирования
setup_logging()

# Настройка безопасности для Swagger UI
security = HTTPBearer()

app = FastAPI(
    title="Система Аутентификации и Авторизации",
    description="Собственная система RBAC с управлением пользователями и правами доступа",
    version="1.0.0",
    # Добавляем схему безопасности для Swagger UI
    openapi_tags=[
        {
            "name": "authentication",
            "description": "Операции аутентификации и авторизации",
        },
        {
            "name": "users",
            "description": "Управление пользователями",
        },
        {
            "name": "admin",
            "description": "Административные операции",
        },
        {
            "name": "resources",
            "description": "Управление ресурсами и проверка разрешений",
        },
    ]
)

# Настройка схемы безопасности для Swagger
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    from fastapi.openapi.utils import get_openapi
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Добавляем схему Bearer токена
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Введите JWT токен, полученный после входа в систему"
        }
    }
    
    # Применяем схему безопасности ко всем endpoint'ам, кроме публичных
    for path_data in openapi_schema["paths"].values():
        for method_data in path_data.values():
            # Пропускаем публичные endpoint'ы (auth, health, root)
            if isinstance(method_data, dict) and "tags" in method_data:
                tags = method_data.get("tags", [])
                if "authentication" not in tags and method_data.get("operationId") not in ["root", "health_check"]:
                    method_data["security"] = [{"BearerAuth": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Регистрация обработчиков исключений
app.add_exception_handler(SystemException, GlobalExceptionHandler.system_exception_handler)
app.add_exception_handler(AuthenticationException, GlobalExceptionHandler.auth_exception_handler)
app.add_exception_handler(AuthorizationException, GlobalExceptionHandler.authorization_exception_handler)
app.add_exception_handler(ValidationException, GlobalExceptionHandler.validation_exception_handler)
app.add_exception_handler(ResourceNotFoundException, GlobalExceptionHandler.resource_not_found_handler)
app.add_exception_handler(SQLAlchemyError, GlobalExceptionHandler.database_exception_handler)
app.add_exception_handler(RequestValidationError, GlobalExceptionHandler.validation_error_handler)

# Добавление middleware для глобальной обработки исключений
app.add_middleware(ExceptionMiddleware)

# Подключение роутеров
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")
app.include_router(resources.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "message": "Система Аутентификации и Авторизации",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "auth": "/api/v1/auth/register",
            "users": "/api/v1/users/me",
            "admin": "/api/v1/admin/stats", 
            "resources": "/api/v1/resources/documents",
        }
    }
