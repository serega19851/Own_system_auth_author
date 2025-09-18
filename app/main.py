# app/main.py
from fastapi import FastAPI
from fastapi.security import HTTPBearer
from app.routers import users, admin, resources, auth

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
