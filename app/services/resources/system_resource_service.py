# app/services/resources/system_resource_service.py

from datetime import datetime
from typing import List

from app.schemas.resources import SystemConfig


class SystemResourceService:
    """Сервис для получения системной конфигурации"""
    
    def __init__(self):
        # Mock данные конфигурации из resources.py
        self.mock_config = [
            {
                "setting_name": "max_login_attempts",
                "setting_value": "5",
                "description": "Максимальное количество попыток входа",
                "last_modified": datetime(2025, 9, 16, 9, 0, 0),
                "modified_by": "admin@test.com"
            },
            {
                "setting_name": "session_timeout",
                "setting_value": "3600",
                "description": "Время жизни сессии в секундах",
                "last_modified": datetime(2025, 9, 16, 8, 30, 0),
                "modified_by": "admin@test.com"
            },
            {
                "setting_name": "password_min_length",
                "setting_value": "8",
                "description": "Минимальная длина пароля",
                "last_modified": datetime(2025, 9, 15, 15, 45, 0),
                "modified_by": "admin@test.com"
            }
        ]
    
    async def get_system_config(self) -> List[SystemConfig]:
        """Получить системную конфигурацию"""
        return [SystemConfig(**cfg) for cfg in self.mock_config]
    
    def _get_default_config(self) -> List[dict]:
        """Получить конфигурацию по умолчанию"""
        return self.mock_config.copy()
