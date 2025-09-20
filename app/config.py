"""
Централизованная конфигурация приложения
Все настройки загружаются из переменных окружения (.env файл)
"""

import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()


class DatabaseConfig:
    """Настройки базы данных"""
    
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql+asyncpg://auth_user:auth_password@localhost:5432/auth_system"
    )


class JWTConfig:
    """Настройки JWT токенов"""
    
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    REFRESH_SECRET_KEY: str = os.getenv("REFRESH_SECRET_KEY", "your-refresh-secret-key-change-in-production")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))


class CookieConfig:
    """Настройки безопасности для cookies"""
    
    COOKIE_SECURE: bool = os.getenv("COOKIE_SECURE", "false").lower() == "true"
    COOKIE_SAMESITE: str = os.getenv("COOKIE_SAMESITE", "lax")
    COOKIE_HTTPONLY: bool = os.getenv("COOKIE_HTTPONLY", "true").lower() == "true"
    
    # Вычисляемые значения на основе JWT настроек
    @classmethod
    def get_cookie_max_age(cls) -> int:
        """Время жизни access cookie в секундах"""
        return JWTConfig.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    
    @classmethod
    def get_refresh_cookie_max_age(cls) -> int:
        """Время жизни refresh cookie в секундах"""
        return JWTConfig.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60


class AppConfig:
    """Общие настройки приложения"""
    
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    APP_NAME: str = "Система Аутентификации и Авторизации"
    VERSION: str = "1.0.0"
    
    # Настройки логирования
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Настройки безопасности
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8080").split(",")
    
    @classmethod
    def is_production(cls) -> bool:
        """Проверка, запущено ли приложение в продакшене"""
        return cls.ENVIRONMENT.lower() == "production"
    
    @classmethod
    def is_development(cls) -> bool:
        """Проверка, запущено ли приложение в разработке"""
        return cls.ENVIRONMENT.lower() == "development"


class Config:
    """Главный класс конфигурации - объединяет все настройки"""
    
    # Подключаем все конфигурации
    db = DatabaseConfig()
    jwt = JWTConfig()
    cookies = CookieConfig()
    app = AppConfig()
    
    @classmethod
    def validate_config(cls) -> bool:
        """Валидация критически важных настроек"""
        errors = []
        
        # Проверяем JWT ключи в продакшене
        if cls.app.is_production():
            if cls.jwt.SECRET_KEY == "your-secret-key-change-in-production":
                errors.append("SECRET_KEY должен быть изменен в продакшене!")
            
            if cls.jwt.REFRESH_SECRET_KEY == "your-refresh-secret-key-change-in-production":
                errors.append("REFRESH_SECRET_KEY должен быть изменен в продакшене!")
            
            if not cls.cookies.COOKIE_SECURE:
                errors.append("COOKIE_SECURE должен быть true в продакшене!")
        
        # Проверяем обязательные настройки
        if not cls.db.DATABASE_URL:
            errors.append("DATABASE_URL обязателен!")
        
        if errors:
            print("❌ ОШИБКИ КОНФИГУРАЦИИ:")
            for error in errors:
                print(f"  - {error}")
            return False
        
        return True
    
    @classmethod
    def print_config(cls) -> None:
        """Вывод текущей конфигурации (без секретных данных)"""
        print("=== КОНФИГУРАЦИЯ ПРИЛОЖЕНИЯ ===\n")
        
        print("🗄️ База данных:")
        print(f"  DATABASE_URL: {cls.db.DATABASE_URL}")
        
        print("\n🔐 JWT:")
        print(f"  ALGORITHM: {cls.jwt.ALGORITHM}")
        print(f"  ACCESS_TOKEN_EXPIRE_MINUTES: {cls.jwt.ACCESS_TOKEN_EXPIRE_MINUTES}")
        print(f"  REFRESH_TOKEN_EXPIRE_DAYS: {cls.jwt.REFRESH_TOKEN_EXPIRE_DAYS}")
        print(f"  SECRET_KEY: {'***' if cls.jwt.SECRET_KEY else 'НЕ УСТАНОВЛЕН'}")
        print(f"  REFRESH_SECRET_KEY: {'***' if cls.jwt.REFRESH_SECRET_KEY else 'НЕ УСТАНОВЛЕН'}")
        
        print("\n🍪 Cookies:")
        print(f"  COOKIE_SECURE: {cls.cookies.COOKIE_SECURE}")
        print(f"  COOKIE_SAMESITE: {cls.cookies.COOKIE_SAMESITE}")
        print(f"  COOKIE_HTTPONLY: {cls.cookies.COOKIE_HTTPONLY}")
        print(f"  COOKIE_MAX_AGE: {cls.cookies.get_cookie_max_age()} сек")
        print(f"  REFRESH_COOKIE_MAX_AGE: {cls.cookies.get_refresh_cookie_max_age()} сек")
        
        print("\n⚙️ Приложение:")
        print(f"  ENVIRONMENT: {cls.app.ENVIRONMENT}")
        print(f"  APP_NAME: {cls.app.APP_NAME}")
        print(f"  VERSION: {cls.app.VERSION}")
        print(f"  LOG_LEVEL: {cls.app.LOG_LEVEL}")


# Глобальный экземпляр конфигурации
config = Config()

# Валидация конфигурации при импорте
if not config.validate_config():
    raise RuntimeError("Критические ошибки в конфигурации приложения!")

if __name__ == "__main__":
   config.print_config() 
