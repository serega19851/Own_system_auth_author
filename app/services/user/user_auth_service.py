# app/services/user_service.py
from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession


from app.models import Role, User
from app.schemas.auth import UserRegister, UserRegisterResponse
from app.auth import PasswordService
from app.repositories.user_repository import UserRepository
from app.repositories.role_repository import RoleRepository
from ..base_service import BaseService
from ...exceptions.business_exceptions import UserException, RoleException


class UserService(BaseService):
    """Сервис для работы с пользователями"""
    
    def __init__(self, db: AsyncSession):
        super().__init__()
        self.db = db
        self.password_service = PasswordService()
        self.user_repository = UserRepository(db)
        self.role_repository = RoleRepository(db)
    
    async def check_email_exists(self, email: str) -> bool:
        """Проверка существования пользователя с данным email"""
        try:
            user = await self.user_repository.get_by_email(email)
            return user is not None
        except Exception as e:
            self._handle_service_error(e, "check_email_exists")
            raise
    
    async def get_default_role(self) -> Role:
        """Получение роли 'user' для новых пользователей"""
        try:
            role = await self.role_repository.get_by_name("user")
            
            if not role:
                raise RoleException("Базовая роль 'user' не найдена в системе", "DEFAULT_ROLE_NOT_FOUND")
            
            return role
        except Exception as e:
            self._handle_service_error(e, "get_default_role")
            raise
    
    async def create_user(self, user_data: UserRegister) -> UserRegisterResponse:
        """Создание нового пользователя"""
        try:
            # 1. Проверка уникальности email
            if await self.check_email_exists(user_data.email):
                raise UserException("Пользователь с таким email уже существует", "EMAIL_ALREADY_EXISTS")
            
            # 2. Хеширование пароля
            hashed_password = self.password_service.hash_password(user_data.password)
            
            # 3. Подготовка данных для создания пользователя
            user_data_dict = {
                "email": user_data.email,
                "password_hash": hashed_password,
                "first_name": user_data.first_name,
                "last_name": user_data.last_name,
                "middle_name": user_data.middle_name,
                "is_active": True,  # Сразу активный (в production можно сделать False до верификации email)
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            # 4. Создание пользователя через репозиторий (базовый метод принимает словарь)
            created_user = await self.user_repository.create(user_data_dict)
            
            # 4. Назначение базовой роли "user"
            await self.assign_default_role(created_user.id)
            
            # 5. Сохранение в БД
            await self.db.commit()
            
            # 6. Формирование ответа
            full_name = f"{user_data.first_name} {user_data.last_name}"
            if user_data.middle_name:
                full_name = f"{user_data.first_name} {user_data.middle_name} {user_data.last_name}"
            
            return UserRegisterResponse(
                id=created_user.id,
                email=created_user.email,
                full_name=full_name,
                message="Пользователь успешно зарегистрирован",
                is_active=created_user.is_active
            )
        except Exception as e:
            self._handle_service_error(e, "create_user")
            raise
    
    async def assign_default_role(self, user_id: int) -> None:
        """Назначение базовой роли пользователю"""
        try:
            default_role = await self.get_default_role()
            
            # Назначение роли через репозиторий
            await self.user_repository.update_user_roles(user_id, [default_role.id])
        except Exception as e:
            self._handle_service_error(e, "assign_default_role")
            raise
    
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Аутентификация пользователя"""
        try:
            # Получение пользователя
            user = await self.user_repository.get_by_email(email)
            
            if not user:
                return None
            
            if not user.is_active:
                return None
            
            if not self.password_service.verify_password(password, user.password_hash):
                return None
            
            return user
        except Exception as e:
            self._handle_service_error(e, "authenticate_user")
            raise
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Получение пользователя по email"""
        try:
            return await self.user_repository.get_by_email(email)
        except Exception as e:
            self._handle_service_error(e, "get_user_by_email")
            raise
