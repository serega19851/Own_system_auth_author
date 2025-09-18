# app/auth.py
import os
from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import HTTPException, status

# Настройки JWT
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
REFRESH_SECRET_KEY = os.getenv("REFRESH_SECRET_KEY", "your-refresh-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7  # Refresh токен живет 7 дней

# Настройки безопасности для cookies
COOKIE_SECURE = os.getenv("ENVIRONMENT", "development") == "production"  # True для HTTPS в продакшене
COOKIE_SAMESITE = os.getenv("COOKIE_SAMESITE", "lax")  # lax, strict, none
COOKIE_HTTPONLY = True  # Всегда True для безопасности
COOKIE_MAX_AGE = ACCESS_TOKEN_EXPIRE_MINUTES * 60  # В секундах
REFRESH_COOKIE_MAX_AGE = REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60  # В секундах

# Настройка хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class PasswordService:
    """Сервис для работы с паролями"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Хеширование пароля с солью"""
        try:
            return pwd_context.hash(password)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка при хешировании пароля"
            )
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Проверка пароля против хеша"""
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception:
            return False
    
    @staticmethod
    def validate_password_strength(password: str) -> bool:
        """Валидация сложности пароля"""
        if len(password) < 8:
            return False
        
        has_letter = any(c.isalpha() for c in password)
        has_digit = any(c.isdigit() for c in password)
        
        return has_letter and has_digit


class JWTService:
    """Сервис для работы с JWT токенами"""
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        """Создание access JWT токена"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "type": "access"})
        
        try:
            encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
            return encoded_jwt
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка при создании access токена"
            )
    
    @staticmethod
    def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None):
        """Создание refresh JWT токена"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        
        to_encode.update({"exp": expire, "type": "refresh"})
        
        try:
            encoded_jwt = jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)
            return encoded_jwt
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка при создании refresh токена"
            )
    
    @staticmethod
    def verify_token(token: str) -> Optional[dict]:
        """Проверка и декодирование access JWT токена"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            if payload.get("type") != "access":
                return None
            return payload
        except JWTError:
            return None
    
    @staticmethod
    def verify_refresh_token(token: str) -> Optional[dict]:
        """Проверка и декодирование refresh JWT токена"""
        try:
            payload = jwt.decode(token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
            if payload.get("type") != "refresh":
                return None
            return payload
        except JWTError:
            return None


class CookieService:
    """Сервис для работы с безопасными cookies"""
    
    @staticmethod
    def get_cookie_settings() -> dict:
        """Получение настроек для безопасных cookies"""
        return {
            "httponly": COOKIE_HTTPONLY,
            "secure": COOKIE_SECURE,
            "samesite": COOKIE_SAMESITE,
            "max_age": COOKIE_MAX_AGE
        }
    
    @staticmethod
    def get_refresh_cookie_settings() -> dict:
        """Получение настроек для refresh cookie"""
        return {
            "httponly": COOKIE_HTTPONLY,
            "secure": COOKIE_SECURE,
            "samesite": COOKIE_SAMESITE,
            "max_age": REFRESH_COOKIE_MAX_AGE
        }


# Фабричные функции для dependency injection
def get_password_service() -> PasswordService:
    """Получение сервиса паролей"""
    return PasswordService()


def get_jwt_service() -> JWTService:
    """Получение сервиса JWT"""
    return JWTService()


def get_cookie_service() -> CookieService:
    """Получение сервиса cookies"""
    return CookieService()