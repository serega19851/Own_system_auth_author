# app/models/resource.py
from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base


class Resource(Base):
    __tablename__ = "resources"
    
    # Основные поля
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    resource_type = Column(String(50), nullable=False, index=True)
    description = Column(String(200))
    is_active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<Resource(id={self.id}, name='{self.name}', type='{self.resource_type}', active={self.is_active})>"
    
    def __str__(self):
        return f"{self.name} ({self.resource_type})"
    
    @classmethod
    def get_by_type(cls, resource_type: str):
        """Получить все ресурсы определенного типа (будет использоваться в будущем)"""
        # Заготовка для будущих проверок доступа
        pass
