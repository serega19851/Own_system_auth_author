# app/services/resources/user_profiles_resource_service.py

from datetime import datetime
from typing import List

from app.schemas.resources import UserProfilePublic


from ..base_service import BaseService

class UserProfilesResourceService(BaseService):
    """Сервис для получения профилей пользователей как ресурса"""
    
    def __init__(self):
        super().__init__()
        # Mock данные профилей из resources.py
        self.mock_profiles = [
            {
                "id": 1,
                "full_name": "Админ Главный Системы",
                "email": "admin@test.com",
                "is_active": True,
                "joined_at": datetime(2025, 9, 15, 10, 0, 0)
            },
            {
                "id": 2,
                "full_name": "Иван Сергеевич Петров",
                "email": "user@test.com",
                "is_active": True,
                "joined_at": datetime(2025, 9, 15, 11, 30, 0)
            },
            {
                "id": 3,
                "full_name": "Анна Викторовна Смирнова",
                "email": "moderator@test.com",
                "is_active": True,
                "joined_at": datetime(2025, 9, 15, 12, 15, 0)
            }
        ]
    
    async def get_user_profiles(self) -> List[UserProfilePublic]:
        """Получить публичные профили пользователей"""
        try:
            return [UserProfilePublic(**profile) for profile in self.mock_profiles]
        except Exception as e:
            self._handle_service_error(e, "get_user_profiles")
            raise
    
    async def get_all_profiles(self) -> List[UserProfilePublic]:
        """Получить все профили пользователей (алиас для совместимости с ResourcesService)"""
        try:
            return await self.get_user_profiles()
        except Exception as e:
            self._handle_service_error(e, "get_all_profiles")
            raise
