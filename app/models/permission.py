# app/models/permission.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base


class Permission(Base):
    __tablename__ = "permissions"
    
    # Основные поля
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    resource_type = Column(String(50), nullable=False, index=True)
    action = Column(String(50), nullable=False, index=True)
    description = Column(String(200))
    
    # Связи
    roles = relationship("Role", secondary="role_permissions", back_populates="permissions")
    
    def __repr__(self):
        return f"<Permission(id={self.id}, name='{self.name}', resource='{self.resource_type}', action='{self.action}')>"
    
    def __str__(self):
        return f"{self.resource_type}_{self.action}"
    
    @classmethod
    def create_name(cls, resource_type: str, action: str) -> str:
        """Создает стандартное имя разрешения в формате resource_type_action"""
        return f"{resource_type}_{action}"
    
    def matches(self, resource_type: str, action: str) -> bool:
        """Проверяет, соответствует ли разрешение указанному ресурсу и действию"""
        return self.resource_type == resource_type and self.action == action
