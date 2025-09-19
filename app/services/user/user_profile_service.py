"""
UserProfileService - сервис для управления пользовательскими профилями
Содержит бизнес-логику для работы с профилем пользователя
"""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.exc import SQLAlchemyError

from ...repositories.user_repository import UserRepository
from ...mappers.system_mappers import SystemMappers
from ...validators.system_validators import SystemValidators, UserNotFoundException
from ...schemas.user import UserProfile, UserUpdate


class UserProfileService:
    """
    Сервис для управления пользовательскими профилями
    Инкапсулирует бизнес-логику работы с профилями пользователей
    """
    
    def __init__(self, 
                 user_repo: UserRepository,
                 mappers: SystemMappers,
                 validators: SystemValidators):
        """
        Инициализация сервиса
        
        Args:
            user_repo: Репозиторий пользователей
            mappers: Мапперы для преобразования данных
            validators: Валидаторы для проверки бизнес-правил
        """
        self.user_repo = user_repo
        self.mappers = mappers
        self.validators = validators
    
    async def get_user_profile(self, user_id: int) -> UserProfile:
        """
        Получить профиль пользователя с ролями и разрешениями
        
        Args:
            user_id: ID пользователя
            
        Returns:
            UserProfile: Профиль пользователя
            
        Raises:
            UserNotFoundException: Если пользователь не найден
        """
        try:
            # Валидация существования пользователя
            await self.validators.validate_user_exists(user_id, self.user_repo)
            
            # Получение пользователя с ролями и разрешениями
            user = await self.user_repo.get_user_with_roles_and_permissions(user_id)
            if not user:
                raise UserNotFoundException(f"Пользователь с ID {user_id} не найден")
            
            # Преобразование в схему профиля
            return self.mappers.user_to_profile_with_permissions(user)
            
        except SQLAlchemyError as e:
            raise Exception(f"Ошибка получения профиля пользователя: {str(e)}")
    
    async def update_user_profile(self, user_id: int, update_data: UserUpdate) -> UserProfile:
        """
        Обновить профиль пользователя
        
        Args:
            user_id: ID пользователя
            update_data: Данные для обновления
            
        Returns:
            UserProfile: Обновленный профиль пользователя
            
        Raises:
            UserNotFoundException: Если пользователь не найден
        """
        try:
            # Валидация возможности обновления пользователя
            await self.validators.validate_user_can_be_updated(user_id, self.user_repo)
            
            # Подготовка данных для обновления
            update_dict = {}
            if update_data.first_name is not None:
                update_dict["first_name"] = update_data.first_name.strip()
            if update_data.last_name is not None:
                update_dict["last_name"] = update_data.last_name.strip()
            if update_data.middle_name is not None:
                update_dict["middle_name"] = update_data.middle_name.strip() if update_data.middle_name else None
            
            if not update_dict:
                # Если данных для обновления нет, просто возвращаем текущий профиль
                return await self.get_user_profile(user_id)
            
            # Добавляем время обновления
            update_dict["updated_at"] = datetime.utcnow()
            
            # Обновление через репозиторий
            updated_user = await self.user_repo.update_user_profile_data(user_id, update_dict)
            if not updated_user:
                raise UserNotFoundException(f"Не удалось обновить пользователя с ID {user_id}")
            
            # Возвращаем обновленный профиль
            return await self.get_user_profile(user_id)
            
        except SQLAlchemyError as e:
            raise Exception(f"Ошибка обновления профиля пользователя: {str(e)}")
    
    async def deactivate_user_account(self, user_id: int) -> Dict[str, Any]:
        """
        Деактивировать аккаунт пользователя (мягкое удаление)
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Dict[str, Any]: Информация о деактивации аккаунта
            
        Raises:
            UserNotFoundException: Если пользователь не найден
        """
        try:
            # Валидация существования пользователя
            await self.validators.validate_user_exists(user_id, self.user_repo)
            
            # Получаем пользователя для информации в ответе
            user = await self.user_repo.get_by_id(user_id)
            if not user:
                raise UserNotFoundException(f"Пользователь с ID {user_id} не найден")
            
            # Деактивация через репозиторий
            success = await self.user_repo.deactivate_user(user_id)
            if not success:
                raise Exception(f"Не удалось деактивировать пользователя с ID {user_id}")
            
            # Формирование ответа
            return {
                "message": "Account successfully deactivated",
                "detail": "Your account has been deactivated. You will no longer be able to log in.",
                "user_id": user_id,
                "email": user.email,
                "deactivated_at": datetime.utcnow().isoformat()
            }
            
        except SQLAlchemyError as e:
            raise Exception(f"Ошибка деактивации аккаунта: {str(e)}") 