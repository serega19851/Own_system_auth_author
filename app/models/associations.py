from sqlalchemy import Table, Column, Integer, ForeignKey
from app.database import Base

# Связующая таблица: Пользователи ↔ Роли (many-to-many)
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True)
)

# Связующая таблица: Роли ↔ Разрешения (many-to-many)  
role_permissions = Table(
    'role_permissions',
    Base.metadata,
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permissions.id'), primary_key=True)
)
