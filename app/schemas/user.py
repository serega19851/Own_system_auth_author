# app/schemas/user.py
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    """Базовая схема пользователя"""
    email: EmailStr
    first_name: str
    last_name: str
    middle_name: Optional[str] = None


class UserCreate(UserBase):
    """Схема для создания пользователя"""
    password: str


class UserUpdate(BaseModel):
    """Схема для обновления пользователя"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    middle_name: Optional[str] = None


class UserResponse(UserBase):
    """Схема ответа с информацией о пользователе"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    roles: List[str] = []  # Список названий ролей
    
    class Config:
        from_attributes = True


class UserProfile(UserResponse):
    """Расширенная схема профиля пользователя"""
    permissions: List[str] = []  # Список разрешений
    
    class Config:
        from_attributes = True
