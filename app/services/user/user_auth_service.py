# app/services/user_service.py
from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from fastapi import HTTPException, status, Depends

from app.models import User, Role
from app.schemas.auth import UserRegister, UserRegisterResponse
from app.auth import PasswordService
from app.core_dependencies import get_db


class UserService:
    """Сервис для работы с пользователями"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.password_service = PasswordService()
    
    async def check_email_exists(self, email: str) -> bool:
        """Проверка существования пользователя с данным email"""
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        return user is not None
    
    async def get_default_role(self) -> Role:
        """Получение роли 'user' для новых пользователей"""
        stmt = select(Role).where(Role.name == "user")
        result = await self.db.execute(stmt)
        role = result.scalar_one_or_none()
        
        if not role:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Базовая роль 'user' не найдена в системе"
            )
        
        return role
    
    async def create_user(self, user_data: UserRegister) -> UserRegisterResponse:
        """Создание нового пользователя"""
        
        # 1. Проверка уникальности email
        if await self.check_email_exists(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Пользователь с таким email уже существует"
            )
        
        # 2. Хеширование пароля
        hashed_password = self.password_service.hash_password(user_data.password)
        
        # 3. Создание пользователя
        new_user = User(
            email=user_data.email,
            password_hash=hashed_password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            middle_name=user_data.middle_name,
            is_active=True,  # Сразу активный (в production можно сделать False до верификации email)
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        self.db.add(new_user)
        await self.db.flush()  # Получаем ID пользователя
        
        # 4. Назначение базовой роли "user"
        await self.assign_default_role(new_user.id)
        
        # 5. Сохранение в БД
        await self.db.commit()
        
        # 6. Формирование ответа
        full_name = f"{user_data.first_name} {user_data.last_name}"
        if user_data.middle_name:
            full_name = f"{user_data.first_name} {user_data.middle_name} {user_data.last_name}"
        
        return UserRegisterResponse(
            id=new_user.id,
            email=new_user.email,
            full_name=full_name,
            message="Пользователь успешно зарегистрирован",
            is_active=new_user.is_active
        )
    
    async def assign_default_role(self, user_id: int) -> None:
        """Назначение базовой роли пользователю"""
        default_role = await self.get_default_role()
        
        # Создание связи user_roles через прямой SQL запрос
        await self.db.execute(
            text("INSERT INTO user_roles (user_id, role_id) VALUES (:user_id, :role_id)"),
            {"user_id": user_id, "role_id": default_role.id}
        )
    
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Аутентификация пользователя"""
        # Получение пользователя с ролями
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            return None
        
        if not user.is_active:
            return None
        
        if not self.password_service.verify_password(password, user.password_hash):
            return None
        
        return user
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Получение пользователя по email"""
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        return user


async def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    """Фабрика для получения сервиса пользователей"""
    return UserService(db)
