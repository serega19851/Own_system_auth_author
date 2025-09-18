# app/schemas/auth.py
from typing import Optional
from pydantic import BaseModel, EmailStr, validator
import re


class UserRegister(BaseModel):
    """Схема для регистрации пользователя"""
    email: EmailStr
    password: str
    password_confirm: str
    first_name: str
    last_name: str
    middle_name: Optional[str] = None

    @validator('password')
    def validate_password_strength(cls, v):
        """Валидация сложности пароля"""
        if len(v) < 8:
            raise ValueError('Пароль должен содержать минимум 8 символов')
        
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('Пароль должен содержать буквы')
        
        if not re.search(r'\d', v):
            raise ValueError('Пароль должен содержать цифры')
        
        return v

    @validator('password_confirm')
    def validate_passwords_match(cls, v, values):
        """Проверка совпадения паролей"""
        if 'password' in values and v != values['password']:
            raise ValueError('Пароли не совпадают')
        return v

    @validator('first_name', 'last_name')
    def validate_name_fields(cls, v):
        """Валидация имени и фамилии"""
        if not v or not v.strip():
            raise ValueError('Поле не может быть пустым')
        
        if len(v.strip()) < 2:
            raise ValueError('Минимальная длина - 2 символа')
        
        return v.strip()

    @validator('middle_name')
    def validate_middle_name(cls, v):
        """Валидация отчества (опционально)"""
        if v and len(v.strip()) < 2:
            raise ValueError('Минимальная длина отчества - 2 символа')
        
        return v.strip() if v else None


class UserRegisterResponse(BaseModel):
    """Ответ после успешной регистрации"""
    id: int
    email: str
    full_name: str
    message: str
    is_active: bool

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    """Схема для входа в систему"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Ответ с токенами"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 1800  # 30 минут в секундах
    user_id: int
    email: str


class RefreshTokenRequest(BaseModel):
    """Запрос на обновление токена"""
    refresh_token: Optional[str] = None  # Опциональный, может браться из cookie


class RefreshTokenResponse(BaseModel):
    """Ответ с новыми токенами после refresh"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 1800  # 30 минут в секундах
