# app/auth.py
from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import HTTPException, status

from app.config import config

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
            expire = datetime.utcnow() + timedelta(minutes=config.jwt.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "type": "access"})
        
        try:
            encoded_jwt = jwt.encode(to_encode, config.jwt.SECRET_KEY, algorithm=config.jwt.ALGORITHM)
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
            expire = datetime.utcnow() + timedelta(days=config.jwt.REFRESH_TOKEN_EXPIRE_DAYS)
        
        to_encode.update({"exp": expire, "type": "refresh"})
        
        try:
            encoded_jwt = jwt.encode(to_encode, config.jwt.REFRESH_SECRET_KEY, algorithm=config.jwt.ALGORITHM)
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
            payload = jwt.decode(token, config.jwt.SECRET_KEY, algorithms=[config.jwt.ALGORITHM])
            if payload.get("type") != "access":
                return None
            return payload
        except JWTError:
            return None
    
    @staticmethod
    def verify_refresh_token(token: str) -> Optional[dict]:
        """Проверка и декодирование refresh JWT токена"""
        try:
            payload = jwt.decode(token, config.jwt.REFRESH_SECRET_KEY, algorithms=[config.jwt.ALGORITHM])
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
            "httponly": config.cookies.COOKIE_HTTPONLY,
            "secure": config.cookies.COOKIE_SECURE,
            "samesite": config.cookies.COOKIE_SAMESITE,
            "max_age": config.cookies.get_cookie_max_age()
        }
    
    @staticmethod
    def get_refresh_cookie_settings() -> dict:
        """Получение настроек для refresh cookie"""
        return {
            "httponly": config.cookies.COOKIE_HTTPONLY,
            "secure": config.cookies.COOKIE_SECURE,
            "samesite": config.cookies.COOKIE_SAMESITE,
            "max_age": config.cookies.get_refresh_cookie_max_age()
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
